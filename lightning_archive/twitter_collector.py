import json
import requests
import os
import csv
import time
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
# Set up directories relative to project root
PROJECT_ROOT = Path(os.path.abspath(__file__)).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw" / "twitter"
METADATA_DIR = DATA_DIR / "metadata"

# Input/Output configuration
INPUT_DIR = DATA_DIR / "raw" / "twitter_api_responses"
DOWNLOAD_FOLDER = RAW_DIR
CSV_FILENAME = METADATA_DIR / "twitter_media_metadata.csv"

# RapidAPI configuration
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = "twitter-api45.p.rapidapi.com"
RAPIDAPI_URL = "https://twitter-api45.p.rapidapi.com/search.php"

# Check if API key is available and warn if not
if not RAPIDAPI_KEY:
    print("\nWARNING: RAPIDAPI_KEY not found in environment variables.")
    print("Twitter API scraping will not work without a valid API key.")
    print("Please add RAPIDAPI_KEY=your_key_here to your .env file.")
    print("You can still process existing Twitter data files if available.")

# Make sure directories exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)  # Make sure the input directory exists

print(f"Project root: {PROJECT_ROOT}")
print(f"Input directory: {INPUT_DIR}")
print(f"Download folder: {DOWNLOAD_FOLDER}")
print(f"Metadata file: {CSV_FILENAME}")

# Target date for proximity scoring (June 26, 2024, 10 PM EST as a central point)
# Convert target to UTC for comparison (EST is UTC-4)
TARGET_DATETIME_EST = datetime(2024, 6, 26, 22, 0, 0, tzinfo=timezone(timedelta(hours=-4)))
TARGET_DATETIME_UTC = TARGET_DATETIME_EST.astimezone(timezone.utc)


# Create the download folder if it doesn't exist (redundant but keeping for clarity)
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
    print(f"Created download directory: {DOWNLOAD_FOLDER}")

# List to hold all metadata records before writing to CSV
metadata_records = []

# --- Scoring Functions ---

def score_resolution(width, height):
    """Scores based on resolution (simple tier system)."""
    if width * height >= 2073600: # 1080p (1920*1080) or higher
        return 3
    elif width * height >= 921600: # 720p (1280*720)
        return 2
    elif width * height > 0:
        return 1
    return 0

def score_timestamp_proximity(tweet_timestamp_str):
    """Scores proximity to the target event time (June 26, 10 PM UTC)."""
    # Example format: 'Sat Jun 23 01:14:58 +0000 2024'
    try:
        # Parse the Twitter timestamp string
        dt_obj = datetime.strptime(tweet_timestamp_str, '%a %b %d %H:%M:%S %z %Y')
        
        # Ensure the parsed object is aware of its timezone (it should be due to %z)
        dt_utc = dt_obj.astimezone(timezone.utc)
        
        time_difference = abs(dt_utc - TARGET_DATETIME_UTC)
        
        # Scoring based on time difference (adjust these tiers as needed)
        if time_difference < timedelta(hours=3):
            return 3 # Very close to the event
        elif time_difference < timedelta(hours=12):
            return 2 # Same day/night
        elif time_difference < timedelta(days=2):
            return 1 # Within a day or two
        return 0
    except Exception:
        return 0

def score_vantage_diversity(geotag):
    """Simple scoring: 2 points for a specific location, 1 point for a generic location."""
    if geotag and geotag != 'No Geo-tag':
        # Check for specific coordinates or detailed place names
        if 'Lat/Long' in geotag or any(k in geotag.lower() for k in ['manhattan', 'brooklyn', 'queens', 'bronx', 'staten island']):
             return 2
        return 1 # Generic location text
    return 0


# --- Extraction, Scoring, and Download Function (REVISED) ---

def process_tweet(tweet):
    """Extracts, scores, and downloads media for a single tweet."""
    
    tweet_id = tweet.get('tweet_id') or tweet.get('id')
    screen_name = tweet.get('screen_name') or tweet.get('user', {}).get('screen_name')
    tweet_url = f"https://twitter.com/{screen_name}/status/{tweet_id}" if screen_name and tweet_id else "URL Not Found"
    
    geotag = 'No Geo-tag'
    
    # Geotag logic (same as previous script)
    geo_data = tweet.get('geo')
    if isinstance(geo_data, dict) and geo_data.get('coordinates'):
        geotag = f"Lat/Long: {geo_data['coordinates'][0]}, {geo_data['coordinates'][1]}"
    elif tweet.get('place') and isinstance(tweet['place'], dict) and tweet['place'].get('full_name'):
        geotag = f"Location: {tweet['place']['full_name']}"

    # Media container check (the fix from the last step)
    media_container = tweet.get('extended_entities') or tweet.get('entities')
    
    # Process and download media if available
    downloaded_paths = []
    if isinstance(media_container, dict) and media_container.get('media'):
        media_list = media_container['media']
        
        for media in media_list:
            base_id = media.get('id_str', 'unknown')
            media_type = media['type']
            media_url = None
            width = media.get('sizes', {}).get('large', {}).get('w', 0)
            height = media.get('sizes', {}).get('large', {}).get('h', 0)
            
            # --- Get Media URL and set filename ---
            if media_type == 'photo':
                media_url = media.get('media_url_https')
                filename = f"{tweet_id}_{base_id}.jpg"
            elif media_type in ('video', 'animated_gif'):
                variants = media.get('video_info', {}).get('variants', [])
                video_variants = [v for v in variants if v.get('bitrate')]
                if video_variants:
                    best_video = max(video_variants, key=lambda x: x.get('bitrate', 0), default={})
                    media_url = best_video.get('url')
                    # Set video resolution from the 'video_info' if available
                    width = media.get('video_info', {}).get('aspect_ratio', [0, 0])[0] # This might be inaccurate; rely on image sizes if possible
                    filename = f"{tweet_id}_{base_id}.mp4"
            
            if media_url:
                local_path = os.path.join(DOWNLOAD_FOLDER, filename)
                
                # --- Download Logic ---
                print(f"  > Downloading {filename}...")
                try:
                    response = requests.get(media_url, stream=True, timeout=30)
                    response.raise_for_status()
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    downloaded_paths.append(local_path)
                except requests.exceptions.RequestException as e:
                    print(f"  !! Failed to download {media_url}: {e}")
                    continue # Move to the next media item
                    
                # --- Scoring ---
                res_score = score_resolution(width, height)
                time_score = score_timestamp_proximity(tweet.get('created_at', ''))
                vantage_score = score_vantage_diversity(geotag)
                total_score = res_score + time_score + vantage_score
                
                # --- Record Metadata ---
                metadata_records.append({
                    'filename': filename,
                    'media_type': media_type,
                    'timestamp': tweet.get('created_at', 'N/A'),
                    'source_url': tweet_url,
                    'geotag': geotag,
                    'resolution_wxh': f"{width}x{height}",
                    'resolution_score': res_score,
                    'timestamp_score': time_score,
                    'vantage_score': vantage_score,
                    'total_score': total_score,
                    'tweet_text': tweet.get('text', '')[:100].replace('\n', ' ') # first 100 chars
                })
                
    return downloaded_paths


# --- Data Loading and Main Processing ---

def process_twitter_data(input_file=None):
    """Process Twitter data from a JSON file and extract media."""
    global metadata_records
    
    # If no specific file is provided, find and process all JSON files
    if input_file is None:
        json_files = list(INPUT_DIR.glob("*.json"))
        if not json_files:
            print(f"No JSON files found in {INPUT_DIR}")
            return
            
        print(f"Found {len(json_files)} Twitter JSON files to process")
        
        # Process each file
        for json_file in json_files:
            print(f"\nProcessing file: {json_file.name}")
            process_single_twitter_file(str(json_file))
            
        return
    else:
        # Process a single specified file
        return process_single_twitter_file(input_file)
        
def process_single_twitter_file(input_file):
    """Process a single Twitter JSON file."""
    global metadata_records
    
    try:
        print(f"Reading Twitter data from: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if this is a legacy format or a newer format
        if 'timeline' in data:
            # Legacy format
            timeline = data.get('timeline', [])
            items_to_process = [tweet for tweet in timeline if tweet.get('type') == 'tweet']
        elif 'data' in data:
            # Newer API format
            items_to_process = data.get('data', [])
        else:
            # Unknown format
            print(f"Warning: Unknown JSON format in {os.path.basename(input_file)}. Looking for 'tweets' key...")
            items_to_process = data.get('tweets', [])
            
        if not items_to_process:
            print(f"No tweets found in the JSON file {os.path.basename(input_file)}")
            return
            
        print(f"Loaded {len(items_to_process)} items from {os.path.basename(input_file)}. Starting processing...")
        print("="*50)

        download_count = 0
    
        for tweet in items_to_process:
            tweet_id = tweet.get('tweet_id') or tweet.get('id')
            if tweet_id:
                print(f"\nProcessing Tweet ID: {tweet_id}")
                paths = process_tweet(tweet)
                
                if paths:
                    download_count += len(paths)
                    print(f"  * Downloaded {len(paths)} files to: {DOWNLOAD_FOLDER}/")
                else:
                    print("  - No downloadable media found in this tweet's JSON structure.")
                
        print("="*50)
        print(f"--- Processing Complete! Total files downloaded: {download_count} ---")
        
        # --- Write to CSV ---
        if metadata_records:
            fieldnames = list(metadata_records[0].keys())
            
            with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(metadata_records)
                
            print(f"Successfully saved {len(metadata_records)} records to {CSV_FILENAME}")
        else:
            print("No media records were found to save to CSV.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found. Please ensure Step 1 was run correctly.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def collect_twitter_media(input_file=None, max_results=20):
    """
    Collects Twitter media from preprocessed JSON data.
    This function is designed to integrate with the main Lightning Archive workflow.
    
    Args:
        input_file: Path to the Twitter JSON data file
        max_results: Maximum number of results to process
        
    Returns:
        A list of dictionaries containing media metadata
    """
    global metadata_records
    metadata_records = []  # Reset metadata records
    
    # Process the Twitter data
    process_twitter_data(input_file)
    
    # Return the collected metadata records
    return metadata_records[:max_results] if max_results else metadata_records


def integrate_with_api_collectors(query="lightning strike NYC June 26 2024", max_results=10, use_rapid_api=True):
    """
    Integration function that mimics the interface of other collectors in api_collectors.py.
    This allows this module to be used alongside YouTube and Reddit collectors.
    
    Args:
        query: Search query to use for Twitter search
        max_results: Maximum number of results to return
        use_rapid_api: Whether to make a fresh API call (True) or use existing files (False)
        
    Returns:
        List of dictionaries containing media metadata in the format expected by api_collectors.py
    """
    global metadata_records
    metadata_records = []  # Reset metadata records
    
    if use_rapid_api and RAPIDAPI_KEY:
        # Format date range for the query (look for content around the lightning event)
        date_range = "since:2024-06-25 until:2024-06-28"
        
        # Search term focusing on NYC lightning with media
        search_term = f"{query} has:media"
        
        # Step 1: Collect fresh data from Twitter API
        print("\n=== STEP 1: COLLECTING TWITTER DATA VIA RAPIDAPI ===")
        json_file = collect_twitter_data(search_term=search_term, date_range=date_range)
        
        if not json_file:
            print("Failed to collect Twitter data via RapidAPI. Falling back to existing files.")
            # Fall back to processing existing files
            process_twitter_data()
        else:
            # Process the newly collected data
            process_twitter_data(json_file)
    else:
        # Just process existing Twitter data files
        if not use_rapid_api:
            print("\n=== PROCESSING EXISTING TWITTER DATA FILES ===")
        else:
            print("\n=== RAPIDAPI_KEY NOT FOUND, USING EXISTING FILES ===")
        process_twitter_data()
    
    # Limit to max_results if specified
    if max_results and len(metadata_records) > max_results:
        # Sort by total_score to get the best media items
        sorted_records = sorted(metadata_records, key=lambda x: int(x.get('total_score', 0)), reverse=True)
        metadata_records = sorted_records[:max_results]
        print(f"Limiting to top {max_results} media items by score")
    
    # Convert to the format expected by api_collectors.py
    formatted_data = []
    for item in metadata_records:
        # Extract tweet ID from filename (first part before underscore)
        tweet_id = item['filename'].split('_')[0]
        
        # Calculate relative path for compatibility with api_collectors
        rel_path = os.path.relpath(
            os.path.join(DOWNLOAD_FOLDER, item['filename']),
            os.path.join(PROJECT_ROOT)
        )
        
        formatted_data.append({
            'platform': 'Twitter',
            'id': tweet_id,
            'title': item['tweet_text'],
            'url': item['source_url'],
            'timestamp': item['timestamp'],
            'misc_data': json.dumps({
                'media_type': item['media_type'],
                'geotag': item['geotag'],
                'resolution': item['resolution_wxh'],
                'resolution_score': item['resolution_score'],
                'timestamp_score': item['timestamp_score'],
                'vantage_score': item['vantage_score'],
                'total_score': item['total_score'],
                'filename': item['filename'],
                'local_path': rel_path
            })
        })
    
    print(f"\nFormatted {len(formatted_data)} Twitter media items for integration")
    return formatted_data
        
# --- Twitter API Data Collection Function ---
def collect_twitter_data(search_term="nyc lightning (video OR photo)", 
                         date_range="since:2024-06-25 until:2024-06-28", 
                         output_filename=None):
    """
    Collect Twitter data using RapidAPI Twitter Search endpoint.
    
    Args:
        search_term: The search term to use
        date_range: Date filter in Twitter format (e.g., "since:2024-06-25 until:2024-06-28")
        output_filename: Optional filename to save results, if None a timestamped file will be used
        
    Returns:
        Path to the saved JSON file or None if the request failed
    """
    if not RAPIDAPI_KEY:
        print("ERROR: RAPIDAPI_KEY is not set in the environment variables.")
        print("Please add it to your .env file: RAPIDAPI_KEY=your_key_here")
        return None
    
    # Create full query with search term and date filter
    full_query = f"{search_term} {date_range}"
    
    # Set up request parameters
    querystring = {"query": full_query}
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    # Set up output filename with timestamp if not provided
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"twitter_search_{timestamp}.json"
    
    # Ensure output path is within our project structure
    output_path = INPUT_DIR / output_filename
    
    try:
        print(f"Attempting to search Twitter with query: {full_query}")
        print(f"Using RapidAPI endpoint: {RAPIDAPI_URL}")
        
        response = requests.get(RAPIDAPI_URL, headers=headers, params=querystring)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the data to a JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        print("-" * 60)
        print(f"API call successful. Twitter data saved to {output_path}")
        print(f"File size: {os.path.getsize(output_path) / 1024:.2f} KB")
        
        # Check if the data contains a timeline
        if 'timeline' in data:
            timeline_count = len(data.get('timeline', []))
            tweet_count = len([item for item in data.get('timeline', []) if item.get('type') == 'tweet'])
            print(f"Number of items in 'timeline': {timeline_count} (tweets: {tweet_count})")
        else:
            print("Note: Response does not contain a 'timeline' field.")
            print(f"Response keys: {list(data.keys())}")
        
        return str(output_path)
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the Twitter API call: {e}")
        if 'response' in locals():
            print(f"Status code: {response.status_code}")
            print(f"Response text: {response.text[:500]}...")
        return None

# --- FULL TWITTER WORKFLOW FUNCTION ---

def full_twitter_workflow(query="lightning strike NYC June 26 2024", 
                          search_term=None, 
                          date_range="since:2024-06-25 until:2024-06-28",
                          max_results=20,
                          save_to_csv=True):
    """
    Complete end-to-end workflow for Twitter data collection and processing.
    
    This function:
    1. Collects Twitter data using RapidAPI (if RAPIDAPI_KEY is available)
    2. Processes the Twitter data and downloads media
    3. Scores and ranks the media based on resolution, timestamp proximity, and location
    4. Returns structured data compatible with the overall Lightning Archive workflow
    
    Args:
        query: Base query text (will be enhanced for Twitter search)
        search_term: Custom search term, if None will be built from query
        date_range: Date filter in Twitter format 
        max_results: Maximum number of results to return
        save_to_csv: Whether to save the final results to a CSV file
        
    Returns:
        List of dictionaries with Twitter media metadata
    """
    print("\n========== TWITTER DATA COLLECTION WORKFLOW ==========")
    print(f"Query: '{query}'")
    print(f"Date range: {date_range}")
    print(f"Max results: {max_results}")
    
    # Step 1: Set up search parameters
    if search_term is None:
        # Enhance the base query for better Twitter results
        search_term = f"{query} has:media"
    
    print(f"\n--- STEP 1: CONFIGURING SEARCH ---")
    print(f"Enhanced search term: '{search_term}'")
    print(f"Date filter: {date_range}")
    
    # Step 2: Collect data from Twitter API (if possible)
    print("\n--- STEP 2: COLLECTING TWITTER DATA ---")
    
    if RAPIDAPI_KEY:
        print("RapidAPI key found, making API request...")
        json_file = collect_twitter_data(search_term=search_term, date_range=date_range)
        
        if json_file:
            print(f"✓ Twitter data collected and saved to {json_file}")
        else:
            print("⚠ Twitter API request failed. Checking for existing data files...")
            json_files = list(INPUT_DIR.glob("*.json"))
            
            if json_files:
                print(f"✓ Found {len(json_files)} existing Twitter data files to process")
            else:
                print("❌ No Twitter data available. Collection failed.")
                return []
    else:
        print("⚠ RAPIDAPI_KEY not found in environment variables")
        print("⚠ Checking for existing Twitter data files...")
        
        json_files = list(INPUT_DIR.glob("*.json"))
        if json_files:
            print(f"✓ Found {len(json_files)} existing Twitter data files to process")
        else:
            print("❌ No Twitter data available and no API key to collect new data.")
            print("Please add RAPIDAPI_KEY to your .env file or provide Twitter data files.")
            return []
    
    # Step 3: Process Twitter data and download media
    print("\n--- STEP 3: PROCESSING TWITTER DATA AND DOWNLOADING MEDIA ---")
    global metadata_records
    metadata_records = []  # Reset metadata records
    
    # Process Twitter data (either from new API request or existing files)
    process_twitter_data()
    
    if not metadata_records:
        print("❌ No media found in Twitter data.")
        return []
        
    print(f"✓ Found {len(metadata_records)} media items in Twitter data")
    
    # Step 4: Score and rank media
    print("\n--- STEP 4: SCORING AND RANKING MEDIA ---")
    
    # Sort by total score to get the best media items
    sorted_records = sorted(metadata_records, key=lambda x: int(x.get('total_score', 0)), reverse=True)
    
    # Limit to max_results
    if max_results and len(sorted_records) > max_results:
        print(f"Limiting to top {max_results} media items by score")
        selected_records = sorted_records[:max_results]
    else:
        selected_records = sorted_records
    
    # Step 5: Format and save results
    print("\n--- STEP 5: FINALIZING RESULTS ---")
    
    # Format data for integration with api_collectors
    formatted_data = []
    for item in selected_records:
        tweet_id = item['filename'].split('_')[0]
        
        # Calculate relative path for compatibility
        rel_path = os.path.relpath(
            os.path.join(DOWNLOAD_FOLDER, item['filename']),
            os.path.join(PROJECT_ROOT)
        )
        
        formatted_data.append({
            'platform': 'Twitter',
            'id': tweet_id,
            'title': item['tweet_text'],
            'url': item['source_url'],
            'timestamp': item['timestamp'],
            'misc_data': json.dumps({
                'media_type': item['media_type'],
                'geotag': item['geotag'],
                'resolution': item['resolution_wxh'],
                'resolution_score': item['resolution_score'],
                'timestamp_score': item['timestamp_score'],
                'vantage_score': item['vantage_score'],
                'total_score': item['total_score'],
                'filename': item['filename'],
                'local_path': rel_path
            })
        })
    
    # Save results to CSV if requested
    if save_to_csv and formatted_data:
        try:
            # Create DataFrame and save to CSV
            df = pd.DataFrame(formatted_data)
            
            # Create metadata directory if it doesn't exist
            os.makedirs(METADATA_DIR, exist_ok=True)
            
            # Generate output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = METADATA_DIR / f"twitter_results_{timestamp}.csv"
            
            # Save to CSV
            df.to_csv(output_path, index=False)
            print(f"✓ Results saved to {output_path}")
        except Exception as e:
            print(f"⚠ Error saving results to CSV: {e}")
    
    print("\n========== TWITTER WORKFLOW COMPLETE ==========")
    print(f"✓ Collected {len(formatted_data)} Twitter media items")
    
    # Return the formatted data for integration with other collectors
    return formatted_data

# --- Command Line Interface ---

def parse_arguments():
    """Parse command line arguments for Twitter collection."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Twitter Media Collection Tool for Lightning Archive")
    
    # Search parameters
    parser.add_argument("--query", type=str, default="lightning strike NYC June 26 2024",
                        help="Base search query")
    parser.add_argument("--search-term", type=str, 
                        help="Custom search term (if not specified, will be built from query)")
    parser.add_argument("--date-range", type=str, default="since:2024-06-25 until:2024-06-28",
                        help="Date range in Twitter format (e.g., 'since:2024-06-25 until:2024-06-28')")
    
    # Output control
    parser.add_argument("--max-results", type=int, default=20,
                        help="Maximum number of results to return")
    parser.add_argument("--no-save-csv", action="store_true",
                        help="Don't save results to CSV")
    
    # Collection mode
    parser.add_argument("--scrape", action="store_true",
                        help="Scrape Twitter data using RapidAPI")
    parser.add_argument("--process", action="store_true", 
                        help="Process Twitter data and download media")
    parser.add_argument("--workflow", action="store_true",
                        help="Run full Twitter workflow (scrape + process)")
    parser.add_argument("--file", type=str,
                        help="Process a specific JSON file")
    
    # Integration mode
    parser.add_argument("--integrate", action="store_true",
                        help="Run in integration mode compatible with api_collectors.py")
    
    return parser.parse_args()

def run_from_command_line():
    """Run Twitter collection from command line with arguments."""
    args = parse_arguments()
    
    if args.integrate:
        # Run in integration mode compatible with api_collectors.py
        return integrate_with_api_collectors(
            query=args.query,
            max_results=args.max_results,
            use_rapid_api=args.scrape
        )
    
    elif args.scrape and args.process:
        # Scrape and process
        print("\n=== TWITTER SCRAPE AND PROCESS ===")
        json_file = collect_twitter_data(
            search_term=args.search_term or f"{args.query} has:media",
            date_range=args.date_range
        )
        if json_file:
            return process_twitter_data(json_file)
        return None
    
    elif args.scrape:
        # Only collect data from API
        print("\n=== TWITTER SCRAPING ===")
        return scrape_twitter_data()
        
    elif args.process:
        # Only process existing data files
        print("\n=== TWITTER DATA PROCESSING ===")
        if args.file:
            return process_single_twitter_file(args.file)
        else:
            return process_twitter_data()
    
    elif args.workflow:
        # Run the full workflow
        print("\n=== FULL TWITTER WORKFLOW ===")
        return full_twitter_workflow(
            query=args.query,
            search_term=args.search_term,
            date_range=args.date_range,
            max_results=args.max_results,
            save_to_csv=not args.no_save_csv
        )
            
    else:
    # If no specific action is specified, run a helpful message
        print("\nNo action specified. Please use one of these options:")
        print("  --scrape       Scrape Twitter data using RapidAPI")
        print("  --process      Process Twitter data and download media")
        print("  --workflow     Run full Twitter workflow (scrape + process)")
        print("  --integrate    Run in integration mode for api_collectors.py")
        print("\nFor a complete list of options, use --help")
        
        return None

# Update the main function to use the command line interface
def main():
    """Run the Twitter media collection process."""
    # Show configuration banner
    print("\n===== Twitter Media Collector =====")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Input directory: {INPUT_DIR}")
    print(f"Download folder: {DOWNLOAD_FOLDER}")
    print(f"Metadata file: {CSV_FILENAME}")
    print("="*50)
    
    # Use command line arguments if provided, otherwise run the default process
    import sys
    
    if len(sys.argv) > 1:
        # Check for direct command line arguments first
        if sys.argv[1] == "--scrape":
            print("\n--- TWITTER API SCRAPING MODE ---")
            json_file = scrape_twitter_data()
            if json_file and len(sys.argv) > 2 and sys.argv[2] == "--process":
                # If --process is specified after --scrape, process the scraped data
                print("\n--- PROCESSING SCRAPED DATA ---")
                process_twitter_data(json_file)
        elif sys.argv[1] == "--process":
            # Process existing files
            print("\n--- PROCESSING EXISTING FILES ---")
            if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
                # If a specific file is provided
                process_twitter_data(sys.argv[2])
            else:
                # Process all files
                process_twitter_data()
        elif sys.argv[1] == "--workflow":
            # Run the full workflow
            print("\n--- RUNNING FULL TWITTER WORKFLOW ---")
            full_twitter_workflow()
        else:
            # Use the command line parser for other arguments
            run_from_command_line()
    else:
        # Default: Show menu for interactive use
        print("\nAvailable options:")
        print("1. Scrape Twitter data using RapidAPI")
        print("2. Process existing Twitter data files")
        print("3. Do both: Scrape and process")
        print("4. Run full Twitter workflow")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice (0-4): ").strip()
            
            if choice == "1":
                scrape_twitter_data()
            elif choice == "2":
                process_twitter_data()
            elif choice == "3":
                json_file = scrape_twitter_data()
                if json_file:
                    print("\nNow processing the scraped data...")
                    process_twitter_data(json_file)
            elif choice == "4":
                full_twitter_workflow()
            elif choice == "0":
                print("Exiting...")
                return
            else:
                print("Invalid choice. Running default process (process existing files).")
                process_twitter_data()
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return
    
    print("\nTwitter media collection complete!")

# --- New Download Function ---

def download_twitter_media(media_data, output_dir=RAW_DIR):
    """
    Download Twitter media (images and videos) from a list of metadata records.
    
    Args:
        media_data: List of dictionaries containing Twitter media metadata
        output_dir: Directory to save downloaded media
        
    Returns:
        List of paths to downloaded media files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_paths = []
    failed_downloads = 0
    
    print(f"\nDownloading {len(media_data)} Twitter media items to {output_dir}...")
    
    for i, item in enumerate(media_data):
        # Extract media URL from the item
        media_url = None
        if 'media_url' in item:
            media_url = item['media_url']
        elif 'url' in item and any(ext in item['url'] for ext in ['.jpg', '.jpeg', '.png', '.mp4']):
            media_url = item['url']
        
        if not media_url:
            print(f"[{i+1}/{len(media_data)}] No media URL found in item, skipping")
            failed_downloads += 1
            continue
            
        # Set filename based on tweet ID and media ID
        filename = item.get('filename')
        if not filename:
            # Generate filename from URL if not provided
            tweet_id = item.get('id', 'unknown')
            extension = os.path.splitext(media_url.split('?')[0])[1] or '.jpg'
            filename = f"{tweet_id}_{int(time.time())}_{i}{extension}"
        
        output_path = os.path.join(output_dir, filename)
        
        # Check if file already exists
        if os.path.exists(output_path):
            print(f"[{i+1}/{len(media_data)}] File {filename} already exists, skipping download")
            downloaded_paths.append(output_path)
            continue
            
        try:
            print(f"[{i+1}/{len(media_data)}] Downloading {media_url}...")
            
            # Set up request with proper headers
            headers = {
                "User-Agent": "LightningArchiveProject/1.0"
            }
            
            # Download the file with timeout and streaming
            response = requests.get(media_url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            downloaded_paths.append(output_path)
            print(f"✓ Downloaded {filename}")
            
            # Wait a bit between downloads to be respectful
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error downloading {media_url}: {e}")
            failed_downloads += 1
    
    success_rate = ((len(media_data) - failed_downloads) / len(media_data)) * 100 if media_data else 0
    print(f"\nTwitter media download summary:")
    print(f"- Total attempted: {len(media_data)}")
    print(f"- Successfully downloaded: {len(downloaded_paths)}")
    print(f"- Failed: {failed_downloads}")
    print(f"- Success rate: {success_rate:.1f}%")
    
    return downloaded_paths

# --- Standalone Twitter API Scraping Function ---
def scrape_twitter_data():
    """
    Standalone function to scrape Twitter data using RapidAPI.
    This matches the functionality provided in the code snippet.
    """
    # --- Target Information ---
    SEARCH_TERM = "nyc lightning (video OR photo)"
    DATE_FILTER = "since:2024-06-25 until:2024-06-28"
    full_query = f"{SEARCH_TERM} {DATE_FILTER}"
    
    # --- API Configuration ---
    url = RAPIDAPI_URL  # Using the URL from our configuration
    
    querystring = {
        "query": full_query
    }
    
    if not RAPIDAPI_KEY:
        print("ERROR: RAPIDAPI_KEY is not set in the environment variables.")
        print("Please add it to your .env file: RAPIDAPI_KEY=your_key_here")
        return None
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    # --- Request Execution and Saving ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_FILENAME = f"nyc_lightning_tweets_{timestamp}.json"
    output_path = INPUT_DIR / OUTPUT_FILENAME
    
    try:
        print(f"Attempting to search with a targeted query: {full_query}")
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        
        data = response.json()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the data to a JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        print("-" * 40)
        print(f"API call successful. Data saved to {output_path}")
        print(f"File size: {os.path.getsize(output_path) / 1024:.2f} KB")
        
        if 'timeline' in data:
            print(f"Number of items in the 'timeline': {len(data.get('timeline', []))}")
            tweet_count = len([item for item in data.get('timeline', []) if item.get('type') == 'tweet'])
            print(f"Number of tweets: {tweet_count}")
        else:
            print("Note: Response does not contain a 'timeline' field.")
            print(f"Response keys: {list(data.keys())}")
        
        return str(output_path)
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API call: {e}")
        if 'response' in locals():
            print(f"Status code: {response.status_code}")
            print(f"Response text: {response.text[:500]}...")
        return None

# Execute the main processing function if script is run directly
if __name__ == "__main__":
    # If argument is provided for direct scraping, do that
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--scrape":
        print("\n===== Twitter API Scraping =====")
        scrape_twitter_data()
    else:
        # Otherwise run the regular main function
        main()