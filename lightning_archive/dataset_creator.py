import os
import pandas as pd
import shutil
import cv2
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from lightning_archive.utils import hash_image, synchronize_timestamps
from lightning_archive.metadata_manager import calculate_score

class DatasetCreator:
    """
    Creates a clean dataset optimized for COLMAP 3D reconstruction
    from the extracted frames and metadata
    """
    
    def __init__(self, metadata_path, screens_folder, output_folder=None):
        """
        Initialize the dataset creator
        
        Args:
            metadata_path: Path to the metadata CSV file
            screens_folder: Folder containing extracted frames from videos/images
            output_folder: Output folder for the processed dataset
                          If None, will default to data/stills
        """
        self.metadata_path = metadata_path
        self.screens_folder = screens_folder
        # Default to data/stills if no output folder provided
        self.output_folder = output_folder if output_folder else os.path.join("data", "stills")
        
        # Create output folders
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Create colmap subdirectories in the output folder
        self.colmap_dir = os.path.join(self.output_folder, "colmap")
        os.makedirs(self.colmap_dir, exist_ok=True)
        os.makedirs(os.path.join(self.colmap_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.colmap_dir, "metadata"), exist_ok=True)
        
        # Load metadata
        self.metadata_df = pd.read_csv(metadata_path)
        
        # Load all available frames
        self.available_frames = self._load_available_frames()
    
    def _load_available_frames(self):
        """Load all available frames from the screens folder"""
        frames = []
        
        if not os.path.exists(self.screens_folder):
            print(f"Screens folder not found: {self.screens_folder}")
            return frames
        
        # Check both YouTube and Twitter subdirectories
        youtube_dir = os.path.join(self.screens_folder, "youtube")
        twitter_dir = os.path.join(self.screens_folder, "twitter")
        
        # Process YouTube frames
        if os.path.exists(youtube_dir):
            for video_dir in os.listdir(youtube_dir):
                video_path = os.path.join(youtube_dir, video_dir)
                if os.path.isdir(video_path):
                    for filename in os.listdir(video_path):
                        if filename.endswith(('.png', '.jpg', '.jpeg')):
                            frames.append(os.path.join(video_path, filename))
        
        # Process Twitter frames
        if os.path.exists(twitter_dir):
            for media_dir in os.listdir(twitter_dir):
                media_path = os.path.join(twitter_dir, media_dir)
                if os.path.isdir(media_path):
                    for filename in os.listdir(media_path):
                        if filename.endswith(('.png', '.jpg', '.jpeg')):
                            frames.append(os.path.join(media_path, filename))
        
        print(f"Found {len(frames)} available frames in {self.screens_folder}")
        return frames
    
    def _calculate_vantage_diversity(self, frames_metadata):
        """
        Calculate a score for the diversity of vantage points
        Higher scores = more diverse vantage points
        """
        # This is a simplified proxy for vantage diversity
        # In a real implementation, this would use geolocation data or image features
        
        # Count unique sources
        unique_sources = set()
        for frame in frames_metadata:
            source = frame.get('source_url', '')
            if source:
                unique_sources.add(source)
        
        # Normalize score between 0 and 1
        diversity_score = min(1.0, len(unique_sources) / max(1, len(frames_metadata)))
        return diversity_score
    
    def _get_image_resolution_score(self, image_path):
        """Get image resolution score (higher is better)"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return 0
            height, width = img.shape[:2]
            # Simple score based on total pixels (normalized to 0-1 scale)
            return min(1.0, (width * height) / 2073600)  # Normalized to 1080p
        except Exception:
            return 0
    
    def _get_frame_timestamp(self, filename):
        """Extract timestamp from filename if possible"""
        try:
            # Extract timestamp from filename (if it contains time_MM_SS.SSS)
            if 'time_' in filename:
                time_part = filename.split('time_')[1].split('.png')[0]
                minutes, seconds = time_part.split('_')
                return float(minutes) * 60 + float(seconds)
            return None
        except:
            return None
    
    def _process_frame(self, frame_path, output_name, frame_index):
        """
        Process an individual frame for the dataset
        
        Args:
            frame_path: Path to the input frame
            output_name: Name for the output file
            frame_index: Index for this frame
            
        Returns:
            Metadata for the processed frame
        """
        # Load the image
        img = cv2.imread(frame_path)
        if img is None:
            print(f"Error loading image: {frame_path}")
            return None
        
        # Get image properties
        height, width = img.shape[:2]
        
        # Create output path - save in colmap subdirectory
        output_path = os.path.join(self.colmap_dir, "images", output_name)
        
        # Save a copy of the image (optionally could enhance/process it here)
        cv2.imwrite(output_path, img)
        
        # Calculate image hash for deduplication
        img_hash = hash_image(output_path)
        
        # Get timestamp from filename if available
        timestamp = self._get_frame_timestamp(os.path.basename(frame_path))
        
        # Get approximate location from the original metadata if available
        location = "NYC"  # Default
        
        # Create frame metadata
        metadata = {
            'filename': output_name,
            'original_path': frame_path,
            'timestamp': timestamp,
            'resolution': f"{width}x{height}",
            'geotags': location,
            'hash': img_hash,
            'frame_index': frame_index
        }
        
        # Find source URL from the original metadata if available
        source_info = self._find_source_info(frame_path)
        if source_info:
            metadata.update(source_info)
        
        return metadata
    
    def _find_source_info(self, frame_path):
        """Find source information for a frame from the original metadata"""
        # Extract base name to try to match with source IDs
        frame_basename = os.path.basename(frame_path)
        
        # Try to find matching source in metadata
        for _, row in self.metadata_df.iterrows():
            if 'local_path' in row and row['local_path']:
                local_path = str(row['local_path'])
                if local_path in frame_path:
                    return {
                        'source_platform': row['platform'],
                        'source_id': row['id'],
                        'source_url': row['url']
                    }
        
        return {}
    
    def create_dataset(self, max_frames=5, min_timestamp_proximity=0.5):
        """
        Create a dataset optimized for COLMAP
        
        Args:
            max_frames: Maximum number of frames to include
            min_timestamp_proximity: Minimum timestamp proximity for frames
            
        Returns:
            Path to the created dataset
        """
        # Check if we have frames
        if not self.available_frames:
            print("No frames available to create dataset")
            return None
        
        print(f"Creating dataset with up to {max_frames} frames")
        
        # Process all frames and collect metadata
        all_frames_metadata = []
        
        for i, frame_path in enumerate(self.available_frames):
            output_name = f"frame_{i:03d}.png"
            metadata = self._process_frame(frame_path, output_name, i)
            if metadata:
                all_frames_metadata.append(metadata)
        
        # Skip if no valid frames
        if not all_frames_metadata:
            print("No valid frames found")
            return None
        
        print(f"Processed {len(all_frames_metadata)} frames")
        
        # Calculate vantage diversity
        vantage_diversity = self._calculate_vantage_diversity(all_frames_metadata)
        print(f"Vantage diversity score: {vantage_diversity:.2f}")
        
        # Score each frame based on resolution, timestamp proximity, and vantage diversity
        scored_frames = []
        
        for frame in all_frames_metadata:
            resolution_score = self._get_image_resolution_score(frame['original_path'])
            
            # Use 0 for timestamp proximity initially
            timestamp_proximity = 0
            
            score = calculate_score(
                resolution=resolution_score,
                timestamp_proximity=timestamp_proximity,
                vantage_diversity=vantage_diversity
            )
            
            frame['score'] = score
            scored_frames.append(frame)
        
        # Sort frames by score (highest first)
        sorted_frames = sorted(scored_frames, key=lambda x: x['score'], reverse=True)
        
        # Select top frames while ensuring minimum timestamp proximity
        selected_frames = []
        for frame in sorted_frames:
            if len(selected_frames) >= max_frames:
                break
                
            # Skip if too close to already selected frames
            if any(abs(frame.get('timestamp', 0) - selected.get('timestamp', 0)) < min_timestamp_proximity 
                  for selected in selected_frames if frame.get('timestamp') and selected.get('timestamp')):
                continue
                
            selected_frames.append(frame)
        
        # Sort selected frames by frame index
        selected_frames.sort(key=lambda x: x['frame_index'])
        
        # Save metadata
        self._save_dataset_metadata(selected_frames)
        
        return self.output_folder
    
    def _save_dataset_metadata(self, frames):
        """Save metadata for the dataset"""
        # Create a DataFrame
        df = pd.DataFrame(frames)
        
        # Ensure metadata directory exists
        os.makedirs(os.path.join(self.output_folder, "metadata"), exist_ok=True)
        
        # Save to CSV
        output_path = os.path.join(self.output_folder, "metadata", "dataset.csv")
        df.to_csv(output_path, index=False)
        
        # Create a COLMAP-friendly format
        colmap_data = {
            "dataset_name": "Lightning Strike NYC June 26 2024",
            "creation_date": datetime.now().isoformat(),
            "num_images": len(frames),
            "images": {}
        }
        
        for i, frame in enumerate(frames):
            colmap_data["images"][i] = {
                "filename": frame["filename"],
                "width": int(frame["resolution"].split("x")[0]),
                "height": int(frame["resolution"].split("x")[1]),
                "source_url": frame.get("source_url", ""),
                "platform": frame.get("source_platform", ""),
            }
        
        # Save as JSON
        json_path = os.path.join(self.colmap_dir, "metadata", "colmap_info.json")
        with open(json_path, "w") as f:
            json.dump(colmap_data, f, indent=2)
        
        print(f"Saved dataset metadata to {output_path} and {json_path}")
        print(f"Created dataset with {len(frames)} frames in {self.output_folder}")
        print(f"COLMAP-ready dataset is in {self.colmap_dir}")

if __name__ == "__main__":
    # Example usage
    metadata_path = "data/metadata/dataset_master.csv"
    screens_folder = "data/screens"
    stills_folder = "data/stills"
    
    creator = DatasetCreator(metadata_path, screens_folder, stills_folder)
    creator.create_dataset(max_frames=5)
