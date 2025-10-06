#!/usr/bin/env python
"""
Script to extract the most useful frames from YouTube videos and Twitter media showing lightning.
This script processes videos/images in:
- data/raw/youtube/ (YouTube videos)
- data/raw/twitter/ (Twitter videos and images)

It extracts frames showing lightning strikes and saves them to:
- data/screens/youtube/ (frames from YouTube videos)
- data/screens/twitter/ (frames from Twitter media)
"""

import os
import sys
from pathlib import Path
import time
import concurrent.futures
from datetime import datetime
import shutil

# Add project root to path to import project modules
project_root = Path(os.path.abspath(__file__)).parent.parent
sys.path.insert(0, str(project_root))

from lightning_archive.frame_extractor import extract_frames_at_peak_brightness, extract_frames_from_image

# Configuration
YOUTUBE_INPUT_DIR = project_root / "data" / "raw" / "youtube"
YOUTUBE_OUTPUT_DIR = project_root / "data" / "screens" / "youtube"

TWITTER_INPUT_DIR = project_root / "data" / "raw" / "twitter"
TWITTER_OUTPUT_DIR = project_root / "data" / "screens" / "twitter"

# Log directories
LOG_DIR = project_root / "data" / "workflow_logs"
YOUTUBE_LOG_DIR = LOG_DIR / "youtube"
TWITTER_LOG_DIR = LOG_DIR / "twitter"

# Common settings
FRAMES_PER_VIDEO = 5  # Number of best frames to extract per video
MIN_FRAME_GAP = 15    # Minimum gap between frames to avoid near-duplicates


def process_youtube_video(video_path):
    """Process a single YouTube video and extract the best frames showing lightning."""
    video_name = video_path.stem
    
    # Create a subdirectory for each video to keep frames organized
    output_subdir = YOUTUBE_OUTPUT_DIR / video_name
    
    print(f"\n{'=' * 80}")
    print(f"Processing YouTube video: {video_path}")
    print(f"Extracting {FRAMES_PER_VIDEO} frames to: {output_subdir}")
    
    try:
        # Extract frames from the video
        frame_paths = extract_frames_at_peak_brightness(
            str(video_path), 
            str(output_subdir),
            num_frames=FRAMES_PER_VIDEO,
            min_frame_gap=MIN_FRAME_GAP
        )
        
        return {
            "source": "YouTube",
            "media": str(video_path),
            "success": True,
            "frames_extracted": len(frame_paths),
            "frame_paths": frame_paths
        }
    except Exception as e:
        print(f"Error processing {video_path}: {e}")
        return {
            "source": "YouTube",
            "media": str(video_path),
            "success": False,
            "error": str(e)
        }


def process_twitter_media(media_path):
    """Process a single Twitter media item (video or image) and extract the best frames showing lightning."""
    media_name = media_path.stem
    
    # Create a subdirectory for each media item to keep frames organized
    output_subdir = TWITTER_OUTPUT_DIR / media_name
    
    print(f"\n{'=' * 80}")
    
    # Check if the file is a video or an image
    file_extension = media_path.suffix.lower()
    is_video = file_extension in ['.mp4', '.mov', '.avi', '.webm']
    
    try:
        if is_video:
            print(f"Processing Twitter video: {media_path}")
            print(f"Extracting {FRAMES_PER_VIDEO} frames to: {output_subdir}")
            
            # Extract frames from the video
            frame_paths = extract_frames_at_peak_brightness(
                str(media_path), 
                str(output_subdir),
                num_frames=FRAMES_PER_VIDEO,
                min_frame_gap=MIN_FRAME_GAP
            )
            
            return {
                "source": "Twitter",
                "media_type": "video",
                "media": str(media_path),
                "success": True,
                "frames_extracted": len(frame_paths),
                "frame_paths": frame_paths
            }
        else:
            # Handle image files
            print(f"Processing Twitter image: {media_path}")
            print(f"Copying image to: {output_subdir}")
            
            # Process the image file
            frame_path = extract_frames_from_image(str(media_path), str(output_subdir))
            
            return {
                "source": "Twitter",
                "media_type": "image",
                "media": str(media_path),
                "success": bool(frame_path),
                "frames_extracted": 1 if frame_path else 0,
                "frame_paths": [frame_path] if frame_path else []
            }
            
    except Exception as e:
        print(f"Error processing {media_path}: {e}")
        return {
            "source": "Twitter",
            "media_type": "unknown",
            "media": str(media_path),
            "success": False,
            "error": str(e)
        }


def process_media_files(media_files, process_func):
    """Process a list of media files with the given processing function."""
    results = []
    
    # Process media files (with optional parallelism)
    use_parallel = False  # Set to True for parallel processing
    
    if use_parallel:
        # Process files in parallel (if you have enough RAM)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = {executor.submit(process_func, media_path): media_path for media_path in media_files}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
    else:
        # Process files serially
        for media_path in media_files:
            result = process_func(media_path)
            results.append(result)
            
    return results


def process_youtube_videos():
    """Process all YouTube videos in the input directory."""
    # Ensure output directory exists
    YOUTUBE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all video files
    video_files = list(YOUTUBE_INPUT_DIR.glob("*.mp4"))
    
    if not video_files:
        print(f"No YouTube video files found in {YOUTUBE_INPUT_DIR}")
        return []
    
    print(f"Found {len(video_files)} YouTube video files to process")
    
    # Process videos
    return process_media_files(video_files, process_youtube_video)


def process_twitter_media_files():
    """Process all Twitter media files in the input directory."""
    # Ensure output directory exists
    TWITTER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all media files (both videos and images)
    video_files = list(TWITTER_INPUT_DIR.glob("*.mp4"))
    image_files = list(TWITTER_INPUT_DIR.glob("*.jpg")) + list(TWITTER_INPUT_DIR.glob("*.png"))
    media_files = video_files + image_files
    
    if not media_files:
        print(f"No Twitter media files found in {TWITTER_INPUT_DIR}")
        return []
    
    print(f"Found {len(media_files)} Twitter media files to process")
    print(f"- {len(video_files)} videos")
    print(f"- {len(image_files)} images")
    
    # Process media files
    return process_media_files(media_files, process_twitter_media)


def generate_log_summary(all_results, start_time):
    """Generate a log summary of the processed media files."""
    # Calculate summary statistics
    total_media = len(all_results)
    success_count = sum(1 for result in all_results if result["success"])
    total_frames = sum(result.get("frames_extracted", 0) for result in all_results)
    
    # Group by source
    youtube_results = [r for r in all_results if r.get("source") == "YouTube"]
    twitter_results = [r for r in all_results if r.get("source") == "Twitter"]
    
    youtube_success = sum(1 for r in youtube_results if r.get("success"))
    twitter_success = sum(1 for r in twitter_results if r.get("success"))
    
    youtube_frames = sum(r.get("frames_extracted", 0) for r in youtube_results)
    twitter_frames = sum(r.get("frames_extracted", 0) for r in twitter_results)
    
    # Twitter media types
    twitter_videos = [r for r in twitter_results if r.get("media_type") == "video"]
    twitter_images = [r for r in twitter_results if r.get("media_type") == "image"]
    
    twitter_video_success = sum(1 for r in twitter_videos if r.get("success"))
    twitter_image_success = sum(1 for r in twitter_images if r.get("success"))
    
    twitter_video_frames = sum(r.get("frames_extracted", 0) for r in twitter_videos)
    twitter_image_frames = sum(r.get("frames_extracted", 0) for r in twitter_images)
    
    # Print summary to console
    print("\n" + "=" * 80)
    print(f"Processing Summary:")
    print(f"Processed {total_media} media files in {time.time() - start_time:.2f} seconds")
    print(f"Successfully processed: {success_count}/{total_media}")
    print(f"Total frames extracted: {total_frames}")
    print("\nBreakdown by source:")
    print(f"- YouTube: {len(youtube_results)} videos, {youtube_success} successful, {youtube_frames} frames")
    print(f"- Twitter: {len(twitter_results)} media files, {twitter_success} successful, {twitter_frames} frames")
    print(f"  - Twitter Videos: {len(twitter_videos)} files, {twitter_video_success} successful, {twitter_video_frames} frames")
    print(f"  - Twitter Images: {len(twitter_images)} files, {twitter_image_success} successful, {twitter_image_frames} frames")
    print("=" * 80)
    
    # Create necessary log directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_DIR.mkdir(exist_ok=True)
    
    # Create source-specific log directories
    youtube_log_dir = LOG_DIR / "youtube"
    twitter_log_dir = LOG_DIR / "twitter"
    youtube_log_dir.mkdir(exist_ok=True)
    twitter_log_dir.mkdir(exist_ok=True)
    
    # Create a combined log file
    combined_log_file = LOG_DIR / f"frame_extraction_{timestamp}.log"
    
    # Create source-specific log files
    youtube_log_file = youtube_log_dir / f"youtube_frames_{timestamp}.log"
    twitter_log_file = twitter_log_dir / f"twitter_frames_{timestamp}.log"
    
    log_files = []
    
    # Write the combined log file
    with open(combined_log_file, "w") as f:
        f.write(f"Frame Extraction Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n")
        f.write(f"Processed {total_media} media files in {time.time() - start_time:.2f} seconds\n")
        f.write(f"Successfully processed: {success_count}/{total_media}\n")
        f.write(f"Total frames extracted: {total_frames}\n")
        f.write("\nBreakdown by source:\n")
        f.write(f"- YouTube: {len(youtube_results)} videos, {youtube_success} successful, {youtube_frames} frames\n")
        f.write(f"- Twitter: {len(twitter_results)} media files, {twitter_success} successful, {twitter_frames} frames\n")
        f.write(f"  - Twitter Videos: {len(twitter_videos)} files, {twitter_video_success} successful, {twitter_video_frames} frames\n")
        f.write(f"  - Twitter Images: {len(twitter_images)} files, {twitter_image_success} successful, {twitter_image_frames} frames\n")
        f.write("=" * 80 + "\n\n")
        
        # Write detailed results for all media
        for result in all_results:
            f.write(f"Source: {result['source']}\n")
            if result['source'] == 'Twitter':
                f.write(f"Media Type: {result.get('media_type', 'unknown')}\n")
            f.write(f"Media: {result['media']}\n")
            f.write(f"Success: {result['success']}\n")
            
            if result['success']:
                f.write(f"Frames extracted: {result['frames_extracted']}\n")
                f.write("Frame paths:\n")
                for path in result.get('frame_paths', []):
                    f.write(f"  - {path}\n")
            else:
                f.write(f"Error: {result.get('error', 'Unknown error')}\n")
            
            f.write("\n")
    
    # Write YouTube-specific log file if there are YouTube results
    if youtube_results:
        with open(youtube_log_file, "w") as f:
            f.write(f"YouTube Frame Extraction Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Processed {len(youtube_results)} YouTube videos in {time.time() - start_time:.2f} seconds\n")
            f.write(f"Successfully processed: {youtube_success}/{len(youtube_results)}\n")
            f.write(f"Total frames extracted: {youtube_frames}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write detailed results for YouTube videos only
            for result in youtube_results:
                f.write(f"Video: {result['media']}\n")
                f.write(f"Success: {result['success']}\n")
                
                if result['success']:
                    f.write(f"Frames extracted: {result['frames_extracted']}\n")
                    f.write("Frame paths:\n")
                    for path in result.get('frame_paths', []):
                        f.write(f"  - {path}\n")
                else:
                    f.write(f"Error: {result.get('error', 'Unknown error')}\n")
                
                f.write("\n")
        log_files.append(youtube_log_file)
    
    # Write Twitter-specific log file if there are Twitter results
    if twitter_results:
        with open(twitter_log_file, "w") as f:
            f.write(f"Twitter Frame Extraction Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Processed {len(twitter_results)} Twitter media files in {time.time() - start_time:.2f} seconds\n")
            f.write(f"Successfully processed: {twitter_success}/{len(twitter_results)}\n")
            f.write(f"Total frames extracted: {twitter_frames}\n")
            f.write(f"Videos: {len(twitter_videos)} files, {twitter_video_success} successful, {twitter_video_frames} frames\n")
            f.write(f"Images: {len(twitter_images)} files, {twitter_image_success} successful, {twitter_image_frames} frames\n")
            f.write("=" * 80 + "\n\n")
            
            # Write detailed results for Twitter media only
            for result in twitter_results:
                f.write(f"Media Type: {result.get('media_type', 'unknown')}\n")
                f.write(f"Media: {result['media']}\n")
                f.write(f"Success: {result['success']}\n")
                
                if result['success']:
                    f.write(f"Frames extracted: {result['frames_extracted']}\n")
                    f.write("Frame paths:\n")
                    for path in result.get('frame_paths', []):
                        f.write(f"  - {path}\n")
                else:
                    f.write(f"Error: {result.get('error', 'Unknown error')}\n")
                
                f.write("\n")
        log_files.append(twitter_log_file)
    
    print(f"Detailed combined log saved to: {combined_log_file}")
    if youtube_results:
        print(f"YouTube-specific log saved to: {youtube_log_file}")
    if twitter_results:
        print(f"Twitter-specific log saved to: {twitter_log_file}")
    
    return log_files


def main():
    """Main function to process all media in the input directories."""
    start_time = time.time()
    
    print("Lightning Archive Frame Extraction Tool")
    print("-------------------------------------")
    print("This script extracts frames showing lightning from YouTube videos and Twitter media")
    
    # Create necessary directories
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    YOUTUBE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    TWITTER_LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process YouTube videos
    print("\nProcessing YouTube videos...")
    youtube_results = process_youtube_videos()
    
    # Process Twitter media
    print("\nProcessing Twitter media...")
    twitter_results = process_twitter_media_files()
    
    # Combine results
    all_results = youtube_results + twitter_results
    
    if not all_results:
        print("\nNo media files were processed. Please check the input directories:")
        print(f"- YouTube videos: {YOUTUBE_INPUT_DIR}")
        print(f"- Twitter media: {TWITTER_INPUT_DIR}")
        return
    
    # Generate log summary
    log_files = generate_log_summary(all_results, start_time)
    
    print("\nLog files generated:")
    for log_file in log_files:
        print(f"- {log_file}")


if __name__ == "__main__":
    main()
