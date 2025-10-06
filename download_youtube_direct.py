#!/usr/bin/env python
"""
Direct YouTube downloader using yt-dlp for the Lightning Archive project.
This script directly downloads YouTube videos from the dataset_master.csv file.
"""

import os
import time
import subprocess
import pandas as pd
import json
from pathlib import Path

def download_with_ytdlp(video_url, output_path):
    """
    Download a YouTube video using yt-dlp
    
    Args:
        video_url: URL of the YouTube video
        output_path: Path where the video should be saved
        
    Returns:
        Success status (True/False)
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check if the file already exists
        if os.path.exists(output_path):
            print(f"Video already exists at {output_path}, skipping download")
            return True
        
        # Build the yt-dlp command
        cmd = [
            'yt-dlp',
            video_url,
            '-o', output_path,
            '-f', 'best[ext=mp4]',  # Try to get the best quality MP4
            '--no-progress',        # Don't show the progress bar (cleaner output)
            '--no-warnings',        # Suppress warnings
            '--no-check-certificate'  # Avoid certificate issues
        ]
        
        # Run the command
        print(f"Downloading {video_url} with yt-dlp...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error downloading {video_url}: {stderr}")
            return False
        
        if os.path.exists(output_path):
            print(f"Successfully downloaded {video_url} to {output_path}")
            return True
        else:
            print(f"Download completed but file not found at {output_path}")
            return False
            
    except Exception as e:
        print(f"Error downloading {video_url}: {e}")
        return False

def download_youtube_videos():
    """Download YouTube videos from dataset_master.csv"""
    # Path to metadata file
    metadata_path = 'data/metadata/dataset_master.csv'
    output_dir = 'data/raw/youtube'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if metadata file exists
    if not os.path.exists(metadata_path):
        print(f"Error: Metadata file not found at {metadata_path}")
        return []
    
    # Read metadata
    try:
        df = pd.read_csv(metadata_path)
    except Exception as e:
        print(f"Error reading metadata file: {e}")
        return []
    
    # Filter for YouTube videos
    youtube_df = df[df['platform'] == 'YouTube']
    youtube_data = youtube_df.to_dict('records')
    
    print(f"\n=== Downloading {len(youtube_data)} YouTube videos ===")
    
    downloaded_paths = []
    
    for i, video in enumerate(youtube_data):
        video_id = video['id']
        video_url = video['url']
        
        output_filename = f"{video_id}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        # Check if video already exists
        if os.path.exists(output_path):
            print(f"[{i+1}/{len(youtube_data)}] Video {video_id} already exists, skipping download")
            downloaded_paths.append(output_path)
            continue
            
        print(f"[{i+1}/{len(youtube_data)}] Downloading {video_url}...")
        
        if download_with_ytdlp(video_url, output_path):
            downloaded_paths.append(output_path)
        
        # Wait a bit between downloads to avoid rate limiting
        time.sleep(1)
    
    # Update metadata with local paths
    update_metadata_with_local_paths(metadata_path, downloaded_paths)
    
    return downloaded_paths

def update_metadata_with_local_paths(metadata_path, downloaded_paths):
    """Update metadata CSV with local file paths"""
    try:
        # Read metadata
        df = pd.read_csv(metadata_path)
        
        # Add local_path column if it doesn't exist
        if 'local_path' not in df.columns:
            df['local_path'] = None
        
        # Update local paths
        for idx, row in df.iterrows():
            if row['platform'] != 'YouTube':
                continue
                
            for path in downloaded_paths:
                if row['id'] in path:
                    df.at[idx, 'local_path'] = path
                    break
        
        # Save updated metadata
        df.to_csv(metadata_path, index=False)
        print(f"Updated metadata CSV with local file paths: {metadata_path}")
    except Exception as e:
        print(f"Error updating metadata with local paths: {e}")

if __name__ == "__main__":
    # Check if yt-dlp is installed
    try:
        subprocess.run(['yt-dlp', '--version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      text=True, 
                      check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("yt-dlp is not installed. Please install it with: pip install yt-dlp")
        exit(1)
        
    print("Using yt-dlp to download YouTube videos...")
    download_youtube_videos()
