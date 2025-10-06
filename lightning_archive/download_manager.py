#!/usr/bin/env python
"""
Unified download manager for Lightning Archive project.
Handles downloading from all supported platforms (YouTube, Twitter, Reddit)
by integrating the specialized downloaders from each collector module.
"""

import os
import time
import pandas as pd
from pathlib import Path
import importlib.util

# Always use the yt-dlp downloader from api_collectors
from lightning_archive.api_collectors import download_youtube_videos as youtube_downloader
print("Using yt-dlp for YouTube downloads")
    
from lightning_archive.twitter_collector import download_twitter_media

def download_all_media_from_metadata(metadata_path, output_dir):
    """
    Download all media from a metadata CSV file
    
    Args:
        metadata_path: Path to the metadata CSV file
        output_dir: Directory to save downloaded media
        
    Returns:
        List of download results with status
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read metadata
    df = pd.read_csv(metadata_path)
    
    results = []
    
    # Group by platform for more efficient processing
    platform_groups = df.groupby('platform')
      # Process YouTube videos
    if 'YouTube' in platform_groups.groups:
        youtube_df = platform_groups.get_group('YouTube')
        youtube_data = youtube_df.to_dict('records')
        print(f"\n=== Downloading {len(youtube_data)} YouTube videos ===")
        youtube_output_dir = os.path.join(output_dir, 'youtube')
        os.makedirs(youtube_output_dir, exist_ok=True)
        
        # Use the specialized YouTube downloader (yt-dlp or pytube)
        downloaded_paths = youtube_downloader(youtube_data, youtube_output_dir)
        
        for i, row in youtube_df.iterrows():
            # Find the matching downloaded path for this ID
            local_path = None
            for path in downloaded_paths:
                if row['id'] in path:
                    local_path = path
                    break
                    
            results.append({
                'platform': 'YouTube',
                'id': row['id'],
                'url': row['url'],
                'local_path': local_path,
                'status': 'success' if local_path else 'failed'
            })
    
    # Process Twitter media
    if 'Twitter' in platform_groups.groups:
        twitter_df = platform_groups.get_group('Twitter')
        twitter_data = []
        
        # Format Twitter data for the twitter_collector downloader
        for i, row in twitter_df.iterrows():
            try:
                misc_data = {}
                if 'misc_data' in row:
                    try:
                        import json
                        misc_data = json.loads(row['misc_data'])
                    except:
                        misc_data = {}
                
                twitter_data.append({
                    'id': row['id'],
                    'url': row['url'],
                    'media_url': misc_data.get('media_url', row['url']),
                    'filename': f"{row['id']}_{misc_data.get('media_id', 'media')}.{misc_data.get('media_type', 'jpg').lower()}"
                })
            except Exception as e:
                print(f"Error processing Twitter row: {e}")
        
        print(f"\n=== Downloading {len(twitter_data)} Twitter media files ===")
        twitter_output_dir = os.path.join(output_dir, 'twitter')
        os.makedirs(twitter_output_dir, exist_ok=True)
        
        # Use the specialized Twitter downloader
        downloaded_paths = download_twitter_media(twitter_data, twitter_output_dir)
        
        for i, row in twitter_df.iterrows():
            # Find the matching downloaded path
            local_path = None
            for path in downloaded_paths:
                if row['id'] in path:
                    local_path = path
                    break
                    
            results.append({
                'platform': 'Twitter',
                'id': row['id'],
                'url': row['url'],
                'local_path': local_path,
                'status': 'success' if local_path else 'failed'
            })
    
    # Process Reddit media (if any)
    if 'Reddit' in platform_groups.groups:
        reddit_df = platform_groups.get_group('Reddit')
        
        # For now, we'll just report these as not implemented
        # Could be extended with Reddit-specific downloader later
        for i, row in reddit_df.iterrows():
            results.append({
                'platform': 'Reddit',
                'id': row['id'],
                'url': row['url'],
                'local_path': None,
                'status': 'not_implemented'
            })
        
        print(f"\n=== Reddit media download not yet implemented for {len(reddit_df)} items ===")
    
    # Create results summary
    success_count = sum(1 for r in results if r['status'] == 'success')
    already_exists = sum(1 for r in results if r['status'] == 'already_exists')
    print(f"\nDownload summary: {success_count + already_exists}/{len(results)} items successfully downloaded")
    print(f"- Successfully downloaded: {success_count}")
    print(f"- Already existed: {already_exists}")
    print(f"- Failed or not implemented: {len(results) - success_count - already_exists}")
    
    # Update metadata CSV with local paths
    update_metadata_with_local_paths(metadata_path, results)
    
    return results

def update_metadata_with_local_paths(metadata_path, download_results):
    """Update metadata CSV with local file paths"""
    try:
        # Read existing metadata
        df = pd.read_csv(metadata_path)
        
        # Create a mapping of id to local path
        path_map = {result['id']: result['local_path'] for result in download_results 
                   if result['local_path'] and result['status'] in ['success', 'already_exists']}
        
        # Add local_path column if it doesn't exist
        if 'local_path' not in df.columns:
            df['local_path'] = None
        
        # Update local paths
        for idx, row in df.iterrows():
            if row['id'] in path_map:
                df.at[idx, 'local_path'] = path_map[row['id']]
        
        # Save updated metadata
        df.to_csv(metadata_path, index=False)
        print(f"Updated metadata CSV with local file paths: {metadata_path}")
    except Exception as e:
        print(f"Error updating metadata with local paths: {e}")

if __name__ == "__main__":
    # Test downloading media from metadata
    metadata_path = 'data/metadata/dataset_master.csv'
    output_dir = 'data/raw'
    
    if os.path.exists(metadata_path):
        download_all_media_from_metadata(metadata_path, output_dir)
    else:
        print(f"Metadata file not found: {metadata_path}")
