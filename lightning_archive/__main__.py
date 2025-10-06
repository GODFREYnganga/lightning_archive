import sys
import os
import argparse
import time
from pathlib import Path
import pandas as pd

from lightning_archive.api_collectors import collect_data, full_collection_workflow
from lightning_archive.download_manager import download_all_media_from_metadata
from lightning_archive.frames_extract import main as extract_frames_main
from lightning_archive.dataset_creator import DatasetCreator

# Define directory structure
DATA_DIR = 'data'
RAW_DIR = os.path.join(DATA_DIR, 'raw')
YOUTUBE_DIR = os.path.join(RAW_DIR, 'youtube')
TWITTER_DIR = os.path.join(RAW_DIR, 'twitter')
SCREENS_DIR = os.path.join(DATA_DIR, 'screens')
STILLS_DIR = os.path.join(DATA_DIR, 'stills')
METADATA_CSV = os.path.join(DATA_DIR, 'metadata', 'dataset_master.csv')
LOGS_DIR = os.path.join(DATA_DIR, 'workflow_logs')

def setup_directories():
    """Create necessary directories"""
    # Define screen directories for YouTube and Twitter
    SCREENS_YOUTUBE_DIR = os.path.join(SCREENS_DIR, 'youtube')
    SCREENS_TWITTER_DIR = os.path.join(SCREENS_DIR, 'twitter')
    
    # Define COLMAP output directories
    COLMAP_IMAGES_DIR = os.path.join(STILLS_DIR, 'colmap', 'images')
    COLMAP_METADATA_DIR = os.path.join(STILLS_DIR, 'colmap', 'metadata')
    
    # Define log directories
    YOUTUBE_LOGS_DIR = os.path.join(LOGS_DIR, 'youtube')
    TWITTER_LOGS_DIR = os.path.join(LOGS_DIR, 'twitter')
    
    # Create all required directories
    for directory in [
        DATA_DIR, 
        RAW_DIR, 
        YOUTUBE_DIR, 
        TWITTER_DIR, 
        STILLS_DIR,
        COLMAP_IMAGES_DIR,
        COLMAP_METADATA_DIR,
        SCREENS_DIR,
        SCREENS_YOUTUBE_DIR,
        SCREENS_TWITTER_DIR,
        os.path.join(DATA_DIR, 'metadata'),
        LOGS_DIR,
        YOUTUBE_LOGS_DIR,
        TWITTER_LOGS_DIR
    ]:
        os.makedirs(directory, exist_ok=True)
    
    print(f"Set up directory structure in {DATA_DIR}")

def collect_phase(query, max_results=30):
    """Run data collection phase"""
    print(f"\n{'='*80}\nPHASE 1: COLLECTING DATA\n{'='*80}")
    
    # Use an expanded set of queries for better coverage
    expanded_queries = [
        query,
        "lightning strike NYC Empire State Building June 26 2024",
        "NYC lightning storm video June 26",
        "Manhattan thunderstorm lightning footage June 2024",
        "Empire State Building hit by lightning June"
    ]
    
    # Remove existing metadata file to start fresh
    if os.path.exists(METADATA_CSV):
        os.remove(METADATA_CSV)
        print(f"Removed existing metadata file: {METADATA_CSV}")
    
    all_results = []
    for i, expanded_query in enumerate(expanded_queries):
        print(f"\nCollecting data for query: '{expanded_query}'")
        
        # First query creates a new file, subsequent queries append to it
        append = (i > 0)
        collect_data(expanded_query, max_results // len(expanded_queries), append=append)
        
        # Give the APIs a break between queries
        time.sleep(2)
    
    if not os.path.exists(METADATA_CSV):
        print(f"Error: Metadata file not created at {METADATA_CSV}")
        return False
        
    # Read the final metadata file to get total count
    try:
        df = pd.read_csv(METADATA_CSV)
        youtube_count = len(df[df['platform'] == 'YouTube'])
        reddit_count = len(df[df['platform'] == 'Reddit'])
        print(f"\nCollection summary:")
        print(f"- YouTube videos: {youtube_count}")
        print(f"- Reddit posts: {reddit_count}")
        print(f"- Total unique items: {len(df)}")
    except Exception as e:
        print(f"Error reading metadata file: {e}")
    
    print("\nData collection phase completed")
    return True

def download_phase():
    """Run media download phase"""
    print(f"\n{'='*80}\nPHASE 2: DOWNLOADING MEDIA\n{'='*80}")
    
    if not os.path.exists(METADATA_CSV):
        print(f"Error: Metadata file not found at {METADATA_CSV}")
        return False
    
    # Download media from all platforms
    download_results = download_all_media_from_metadata(METADATA_CSV, RAW_DIR)
    
    # Check results
    success_count = sum(1 for r in download_results if r['status'] in ['success', 'already_exists'])
    print(f"\nDownloaded {success_count} out of {len(download_results)} media files")
    
    return success_count > 0

def extract_phase():
    """Run frame extraction phase"""
    print(f"\n{'='*80}\nPHASE 3: EXTRACTING FRAMES\n{'='*80}")
    
    # Use the dedicated frames_extract module to handle both YouTube and Twitter media
    try:
        print("Running frames_extract to process YouTube videos and Twitter media...")
        extract_frames_main()  # This handles both YouTube and Twitter media
        
        # Get paths to screens directories
        youtube_screens = os.path.join(SCREENS_DIR, 'youtube')
        twitter_screens = os.path.join(SCREENS_DIR, 'twitter')
        
        youtube_frame_count = 0
        twitter_frame_count = 0
        
        # Count YouTube frames
        if os.path.exists(youtube_screens):
            for video_dir in os.listdir(youtube_screens):
                video_path = os.path.join(youtube_screens, video_dir)
                if os.path.isdir(video_path):
                    youtube_frame_count += len([f for f in os.listdir(video_path) 
                                              if f.endswith(('.png', '.jpg', '.jpeg'))])
        
        # Count Twitter frames
        if os.path.exists(twitter_screens):
            for media_dir in os.listdir(twitter_screens):
                media_path = os.path.join(twitter_screens, media_dir)
                if os.path.isdir(media_path):
                    twitter_frame_count += len([f for f in os.listdir(media_path) 
                                             if f.endswith(('.png', '.jpg', '.jpeg'))])
        
        total_frames = youtube_frame_count + twitter_frame_count
        
        print(f"\nExtracted frames summary:")
        print(f"- YouTube frames: {youtube_frame_count}")
        print(f"- Twitter frames: {twitter_frame_count}")
        print(f"- Total frames: {total_frames}")
        
        return total_frames > 0
    
    except Exception as e:
        print(f"Error during frame extraction: {e}")
        print("Frame extraction failed. Check if media files exist in raw/youtube/ and raw/twitter/ directories.")
        return False

def create_dataset_phase():
    """Run dataset creation phase"""
    print(f"\n{'='*80}\nPHASE 4: CREATING FINAL DATASET\n{'='*80}")
    
    # Create dataset for COLMAP - input from screens folder, output to stills folder
    creator = DatasetCreator(METADATA_CSV, SCREENS_DIR, STILLS_DIR)
    dataset_path = creator.create_dataset(max_frames=10)  # Increased max frames for better results
    
    if not dataset_path:
        print("Error creating dataset")
        return False
    
    # Check for output files in the colmap subdirectory
    colmap_images_dir = os.path.join(STILLS_DIR, "colmap", "images")
    if os.path.exists(colmap_images_dir):
        image_count = len([f for f in os.listdir(colmap_images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
        print(f"\nCreated final dataset with {image_count} images at {dataset_path}")
        print(f"COLMAP-ready dataset is in {os.path.join(STILLS_DIR, 'colmap')}")
        print(f"The dataset is now ready for COLMAP 3D reconstruction")
        return image_count > 0
    else:
        print(f"Warning: No images found in {colmap_images_dir}")
        return False

def generate_report():
    """Generate a summary report of the dataset"""
    print(f"\n{'='*80}\nFINAL REPORT\n{'='*80}")
    
    # Check metadata
    if os.path.exists(METADATA_CSV):
        try:
            import pandas as pd
            df = pd.read_csv(METADATA_CSV)
            
            # Platform distribution
            platform_counts = df['platform'].value_counts()
            print("\nPlatform distribution:")
            for platform, count in platform_counts.items():
                print(f"  - {platform}: {count} items")
            
            # Media with local paths
            if 'local_path' in df.columns:
                downloaded = df['local_path'].notna().sum()
                print(f"\nMedia downloaded: {downloaded} out of {len(df)} items")
              # Count frames in screens directory
            
            # Count extracted frames in screens directory
            youtube_frames = 0
            twitter_frames = 0
            
            youtube_dir = os.path.join(SCREENS_DIR, 'youtube')
            twitter_dir = os.path.join(SCREENS_DIR, 'twitter')
            
            if os.path.exists(youtube_dir):
                for video_dir in os.listdir(youtube_dir):
                    video_path = os.path.join(youtube_dir, video_dir)
                    if os.path.isdir(video_path):
                        youtube_frames += len([f for f in os.listdir(video_path) 
                                            if f.endswith(('.png', '.jpg', '.jpeg'))])
            
            if os.path.exists(twitter_dir):
                for media_dir in os.listdir(twitter_dir):
                    media_path = os.path.join(twitter_dir, media_dir)
                    if os.path.isdir(media_path):
                        twitter_frames += len([f for f in os.listdir(media_path) 
                                            if f.endswith(('.png', '.jpg', '.jpeg'))])
                                            
            total_extracted = youtube_frames + twitter_frames
            print(f"\nExtracted frames: {total_extracted}")
            print(f"- YouTube: {youtube_frames}")
            print(f"- Twitter: {twitter_frames}")
            
            # COLMAP dataset
            colmap_images_dir = os.path.join(STILLS_DIR, "colmap", "images") 
            colmap_images = len([f for f in os.listdir(colmap_images_dir) 
                              if f.endswith(('.png', '.jpg', '.jpeg'))]) if os.path.exists(colmap_images_dir) else 0
            print(f"\nFinal dataset images: {colmap_images}")
            
        except Exception as e:
            print(f"Error generating report from metadata: {e}")
    
    print("\nLightning Archive processing complete!")
    print("Use the created dataset with COLMAP for 3D reconstruction of the lightning strike")

def run_full_workflow(query, max_results=30):
    """Run the complete workflow"""
    setup_directories()
    
    # Phase 1: Collect data
    if not collect_phase(query, max_results):
        print("Data collection failed, stopping workflow")
        return
    
    # Phase 2: Download media
    if not download_phase():
        print("Media download failed, stopping workflow")
        return
    
    # Phase 3: Extract frames
    if not extract_phase():
        print("Frame extraction failed, stopping workflow")
        return
    
    # Phase 4: Create dataset
    if not create_dataset_phase():
        print("Dataset creation failed, stopping workflow")
        return
    
    # Generate report
    generate_report()

def analyze_twitter_responses():
    """Analyze saved Twitter API responses to understand their structure"""
    print(f"\n{'='*80}\nANALYZING TWITTER API RESPONSES\n{'='*80}")
    
    # Default directory for saved responses
    response_dir = os.path.join(RAW_DIR, 'twitter_api_responses')
    
    # Create directory if it doesn't exist
    os.makedirs(response_dir, exist_ok=True)
    
    # Check if there are any response files
    response_files = [f for f in os.listdir(response_dir) if f.endswith('.json')]
    
    if response_files:
        print(f"Found {len(response_files)} Twitter API response files in {response_dir}")
        print("These files contain the raw data from Twitter API queries")
        for file in response_files[:5]:  # Show up to 5 files
            print(f"- {file}")
        if len(response_files) > 5:
            print(f"...and {len(response_files) - 5} more files")
    else:
        print("No Twitter API response files found.")
        print("Run the Twitter data collection scripts first to generate response files.")

def main():
    """Main entry point with command-line argument parsing"""
    parser = argparse.ArgumentParser(description='Lightning Archive Tool')
    
    parser.add_argument('--query', type=str, default="lightning strike NYC June 26 2024",
                        help='Search query for data collection')
    parser.add_argument('--max-results', type=int, default=30,
                        help='Maximum number of results to fetch per platform')
    parser.add_argument('--phase', type=str, 
                        choices=['search_only', 'collect', 'download', 'extract', 'dataset', 'all'],
                        default='all', help='Run a specific phase of the workflow')
    
    args = parser.parse_args()
    
    print(f"Lightning Archive Tool - v0.3.0")
    print(f"Query: {args.query}")
    print(f"Max results: {args.max_results}")
    print(f"Selected phase: {args.phase}")    # Run the selected phase
    if args.phase == 'search_only':
        print(f"\n{'='*80}\nSEARCH ONLY PHASE\n{'='*80}")
        setup_directories()
        from lightning_archive.api_collectors import full_collection_workflow
        result_df = full_collection_workflow(args.query, args.max_results, download=False)
        
        # Display a summary of what we collected
        if not result_df.empty:
            youtube_count = len(result_df[result_df['platform'] == 'YouTube'])
            reddit_count = len(result_df[result_df['platform'] == 'Reddit'])
            print(f"\nSearch results summary:")
            print(f"- YouTube videos found: {youtube_count}")
            print(f"- Reddit posts found: {reddit_count}")
            print(f"- Total unique items: {len(result_df)}")
            print(f"\nData saved to: {METADATA_CSV}")
        
        print("Search only phase completed. You can now run the download phase separately.")
    elif args.phase == 'collect':
        collect_phase(args.query, args.max_results)
    elif args.phase == 'download':
        download_phase()
    elif args.phase == 'extract':
        extract_phase()
    elif args.phase == 'dataset':
        create_dataset_phase()
    else:  # 'all'
        run_full_workflow(args.query, args.max_results)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"\nTotal execution time: {time.time() - start_time:.2f} seconds")
