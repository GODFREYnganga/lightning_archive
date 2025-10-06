#!/usr/bin/env python
"""
Direct script to extract frames from videos and images showing lightning.
This script bypasses module imports to directly extract frames.
"""

import os
import cv2
import numpy as np
from pathlib import Path
import shutil
from datetime import datetime
import time
import concurrent.futures
import sys

def extract_frames_at_peak_brightness(video_path, output_folder, num_frames=5, min_frame_gap=15):
    """
    Extract frames from a video at points of peak brightness (likely lightning strikes).
    
    Args:
        video_path (str): Path to the video file
        output_folder (str): Directory where extracted frames will be saved
        num_frames (int): Number of frames to extract (default: 5)
        min_frame_gap (int): Minimum gap between frames in seconds (default: 15)
    
    Returns:
        list: List of paths to the extracted frames
    """
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Get the base filename without extension
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Could not open video file: {video_path}")
        return []
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    print(f"Processing video: {os.path.basename(video_path)}")
    print(f"  - Duration: {duration:.1f} seconds")
    print(f"  - Frame count: {frame_count}")
    print(f"  - FPS: {fps}")
    
    # Calculate the frame gap in frames
    min_frame_gap_frames = int(min_frame_gap * fps)
    
    # Store brightness values and frame numbers
    brightness_data = []
    
    # Process video frames to calculate brightness values
    frame_number = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Calculate brightness (mean pixel value)
        brightness = np.mean(frame)
        brightness_data.append((frame_number, brightness))
        
        frame_number += 1
        
        # Print progress every 500 frames
        if frame_number % 500 == 0:
            print(f"  - Processed {frame_number}/{frame_count} frames ({frame_number/frame_count*100:.1f}%)")
    
    # Close the video capture
    cap.release()
    
    if not brightness_data:
        print(f"No frames processed in video: {video_path}")
        return []
    
    # Sort by brightness (descending)
    brightness_data.sort(key=lambda x: x[1], reverse=True)
    
    # Get the frames with highest brightness, ensuring min_frame_gap between them
    selected_frames = []
    for frame_number, brightness in brightness_data:
        # Check if this frame is far enough from already selected frames
        if all(abs(frame_number - selected) >= min_frame_gap_frames for selected in selected_frames):
            selected_frames.append(frame_number)
            if len(selected_frames) >= num_frames:
                break
    
    # Sort frames by their order in the video
    selected_frames.sort()
    
    # Extract the selected frames
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Could not reopen video file: {video_path}")
        return []
    
    saved_frames = []
    
    for i, frame_number in enumerate(selected_frames):
        # Set the position to the selected frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # Read the frame
        ret, frame = cap.read()
        if not ret:
            print(f"Could not read frame {frame_number}")
            continue
        
        # Create filename with frame number and timestamp
        timestamp = frame_number / fps
        minutes = int(timestamp / 60)
        seconds = timestamp % 60
        
        filename = f"{base_name}_frame{i+1}_at_{minutes:02d}m{seconds:05.2f}s.jpg"
        output_path = os.path.join(output_folder, filename)
        
        # Save the frame as JPEG
        cv2.imwrite(output_path, frame)
        saved_frames.append(output_path)
        
        print(f"  - Saved frame {i+1}/{len(selected_frames)}: {filename}")
    
    # Close the video capture
    cap.release()
    
    print(f"Extracted {len(saved_frames)} frames from {os.path.basename(video_path)}")
    return saved_frames

def extract_frames_from_image(image_path, output_folder):
    """
    Copy and rename an image file to standardized frame format.
    
    Args:
        image_path (str): Path to the image file
        output_folder (str): Directory where the image will be copied
    
    Returns:
        list: List containing the path to the copied image
    """
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Get the base filename without extension
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Create new filename
    new_filename = f"{base_name}_frame.jpg"
    output_path = os.path.join(output_folder, new_filename)
    
    # Copy the image
    shutil.copy2(image_path, output_path)
    
    print(f"Copied image: {os.path.basename(image_path)} -> {new_filename}")
    return [output_path]

def process_directory(input_dir, output_dir):
    """Process all video and image files in a directory"""
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Input directory does not exist: {input_dir}")
        return []
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all files in the directory
    files = os.listdir(input_dir)
    
    # Filter for video and image files
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    videos = [f for f in files if os.path.splitext(f)[1].lower() in video_extensions]
    images = [f for f in files if os.path.splitext(f)[1].lower() in image_extensions]
    
    print(f"Found {len(videos)} videos and {len(images)} images in {input_dir}")
    
    all_results = []
    
    # Process videos - each video gets its own folder
    for video in videos:
        video_path = os.path.join(input_dir, video)
        try:
            # Create a folder for this specific video (using basename without extension)
            video_basename = os.path.splitext(video)[0]
            video_output_dir = os.path.join(output_dir, video_basename)
            os.makedirs(video_output_dir, exist_ok=True)
            
            print(f"Processing video: {video} → Output folder: {video_output_dir}")
            results = extract_frames_at_peak_brightness(video_path, video_output_dir)
            all_results.extend(results)
        except Exception as e:
            print(f"Error processing video {video}: {e}")
    
    # Process images - each image gets its own folder
    for image in images:
        image_path = os.path.join(input_dir, image)
        try:
            # Create a folder for this specific image (using basename without extension)
            image_basename = os.path.splitext(image)[0]
            image_output_dir = os.path.join(output_dir, image_basename)
            os.makedirs(image_output_dir, exist_ok=True)
            
            print(f"Processing image: {image} → Output folder: {image_output_dir}")
            results = extract_frames_from_image(image_path, image_output_dir)
            all_results.extend(results)
        except Exception as e:
            print(f"Error processing image {image}: {e}")
    
    return all_results

def main():
    """Main function to process YouTube videos and Twitter media"""
    project_root = Path(os.path.abspath(__file__)).parent
    
    # Configuration
    YOUTUBE_INPUT_DIR = project_root / "data" / "raw" / "youtube"
    YOUTUBE_OUTPUT_DIR = project_root / "data" / "screens" / "youtube"

    TWITTER_INPUT_DIR = project_root / "data" / "raw" / "twitter"
    TWITTER_OUTPUT_DIR = project_root / "data" / "screens" / "twitter"
    
    # Ensure output directories exist
    os.makedirs(YOUTUBE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(TWITTER_OUTPUT_DIR, exist_ok=True)
    
    print("\n===== Processing YouTube videos =====")
    youtube_results = process_directory(YOUTUBE_INPUT_DIR, YOUTUBE_OUTPUT_DIR)
    
    print("\n===== Processing Twitter media =====")
    twitter_results = process_directory(TWITTER_INPUT_DIR, TWITTER_OUTPUT_DIR)
    
    print("\n===== Summary =====")
    print(f"Extracted {len(youtube_results)} frames from YouTube videos")
    print(f"Extracted {len(twitter_results)} frames from Twitter media")
    print(f"Total frames extracted: {len(youtube_results) + len(twitter_results)}")
    
    return youtube_results + twitter_results

if __name__ == "__main__":
    main()
