#!/usr/bin/env python
"""
Test script for YouTube downloads using the updated api_collectors.py module
"""

import os
from lightning_archive.api_collectors import download_youtube_videos

def test_youtube_download():
    # Create test data
    test_video_data = [
        {
            'id': 'test_video_1',
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'  # A famous video that should be available
        }
    ]
    
    # Set output directory
    output_dir = 'data/raw/youtube/test'
    os.makedirs(output_dir, exist_ok=True)
    
    print("Testing YouTube download with yt-dlp...")
    download_paths = download_youtube_videos(test_video_data, output_dir)
    
    if download_paths:
        print(f"Success! Downloaded {len(download_paths)} videos.")
        for path in download_paths:
            print(f"- {path}")
    else:
        print("No videos were downloaded. Please check the error messages above.")
    
    return len(download_paths) > 0

if __name__ == "__main__":
    test_youtube_download()
