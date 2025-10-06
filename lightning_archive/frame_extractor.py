#!/usr/bin/env python
"""
Functions for extracting frames from videos and images showing lightning.
This module provides utilities for:
1. Processing videos to extract frames at peak brightness (likely lightning strikes)
2. Processing images to copy and rename them to standardized frame format
"""

import os
import cv2
import numpy as np
from pathlib import Path
import shutil
from datetime import datetime
import re

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
    
    # Get the basename of the video file (without path or extension)
    video_basename = os.path.basename(os.path.splitext(video_path)[0])
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    print(f"Video FPS: {fps}")
    print(f"Frame count: {frame_count}")
    print(f"Duration: {duration:.2f} seconds")
    
    # Calculate minimum frame gap
    min_frame_gap_frames = int(min_frame_gap * fps)
    
    # Process video frames
    frame_brightnesses = []
    current_frame = 0
    
    while current_frame < frame_count:
        # Set position and read frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Calculate frame brightness
        # Convert to grayscale and calculate mean brightness
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        # Store frame info
        frame_brightnesses.append((current_frame, brightness))
        
        # Skip frames for efficiency
        # We don't need to analyze every frame, can jump forward
        current_frame += max(1, int(fps / 4))  # Check 4 frames per second
    
    # Find frames with peak brightness
    # Sort by brightness (descending)
    frame_brightnesses.sort(key=lambda x: x[1], reverse=True)
    
    # Extract the brightest frames, ensuring min_frame_gap between them
    selected_frames = []
    extracted_frame_paths = []
    
    for frame_idx, brightness in frame_brightnesses:
        # Check if this frame is far enough from already selected frames
        if all(abs(frame_idx - prev_idx) >= min_frame_gap_frames for prev_idx in selected_frames):
            selected_frames.append(frame_idx)
            
            # Extract the frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                # Generate filename with timestamp
                timestamp = frame_idx / fps
                minutes = int(timestamp / 60)
                seconds = int(timestamp % 60)
                
                # Get the base name of the video file
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                
                # Create a filename with the video name, frame index, and brightness level
                frame_path = os.path.join(
                    output_folder, 
                    f"{video_name}_frame_{frame_idx:06d}_{minutes:02d}m{seconds:02d}s_bright{brightness:.2f}.jpg"
                )
                
                # Save frame
                cv2.imwrite(frame_path, frame)
                extracted_frame_paths.append(frame_path)
                
                print(f"Extracted frame {len(extracted_frame_paths)}/{num_frames}: {frame_path}")
                
                # Break if we've extracted enough frames
                if len(selected_frames) >= num_frames:
                    break
    
    # Release the video capture
    cap.release()
    
    print(f"Extracted {len(extracted_frame_paths)} frames from {video_path}")
    return extracted_frame_paths


def extract_frames_from_image(image_path, output_folder):
    """
    Process a single image by copying it to the output directory with a standardized filename.
    
    Args:
        image_path (str): Path to the image file
        output_folder (str): Directory where the processed image will be saved
    
    Returns:
        str: Path to the processed image or None if processing failed
    """
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Read the image to verify it's valid
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not read image file: {image_path}")
            return None
        
        # Get image brightness (to maintain similar metadata as video frames)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        # Get the base name of the image file
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Create a filename with the image name and brightness level
        output_path = os.path.join(
            output_folder, 
            f"{image_name}_bright{brightness:.2f}.jpg"
        )
        
        # Save image (using cv2 to ensure consistent format)
        cv2.imwrite(output_path, img)
        print(f"Processed image: {output_path}")
        
        return output_path
    
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None
