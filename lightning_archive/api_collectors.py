import os
import requests 
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv
import json
import time 
import tempfile
import praw
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# --- NATIVE API KEYS ---
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

# --- YOUTUBE COLLECTOR (Native API) ---
class YouTubeCollector:
    """Collect videos using YouTube Data API v3"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.video_ids_seen = set()
    
    def get_video_details(self, video_id):
        """Get detailed information about a specific video"""
        url = f"{self.base_url}/videos"
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('items'):
                return None
            
            item = data['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            
            view_count = int(statistics.get('viewCount', 0))
            
            # Calculate relevance score
            relevance_score = 0
            title = snippet['title'].lower()
            date_terms = ['june 26', 'june 2024', '6/26', '26th june', '06/26']
            
            # Videos with "NYC" + "lightning" in title get highest score
            if 'nyc' in title and 'lightning' in title:
                relevance_score += 100
            # Videos with "Empire State" and "lightning" get high score
            elif 'empire state' in title and 'lightning' in title:
                relevance_score += 80
            # Videos that explicitly mention the date in title get bonus
            elif any(term in title for term in date_terms):
                relevance_score += 50
            
            # Add view count as a factor (more views = more likely to be good quality)
            view_score = min(view_count / 1000, 50)  # Cap at 50 points
            total_score = relevance_score + view_score
            
            return {
                'platform': 'YouTube',
                'id': video_id,
                'title': snippet['title'],
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'timestamp': snippet['publishedAt'],
                'misc_data': json.dumps({
                    'channelId': snippet['channelId'],
                    'description': snippet.get('description', ''),
                    'viewCount': view_count,
                    'likeCount': statistics.get('likeCount', '0'),
                    'duration': item.get('contentDetails', {}).get('duration', ''),
                    'relevance_score': total_score
                })            }
        except Exception as e:
            print(f"Error getting video details for {video_id}: {e}")
            return None
    
    def search_videos(self, query, max_results=20):
        """Search YouTube for videos matching the query"""
        print(f"🔍 Searching: '{query}'")
        
        # Define an expanded date range for filtering
        published_after = "2024-06-26T00:00:00Z"
        published_before = "2024-06-28T23:59:59Z"
        
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'publishedAfter': published_after,
            'publishedBefore': published_before,
            'maxResults': min(max_results + 10, 50),  # Get extra for filtering
            'key': self.api_key,
            'order': 'relevance',
            'relevanceLanguage': 'en',
            'videoDuration': 'short'  # Prefer short videos
        }
        
        try:
            response = requests.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                print(f"   ❌ API Error: {data['error']['message']}")
                return []
            
            videos = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                
                # Skip if we've already seen this video
                if video_id in self.video_ids_seen:
                    continue
                
                self.video_ids_seen.add(video_id)
                
                # Get detailed information
                video_info = self.get_video_details(video_id)
                if video_info:
                    videos.append(video_info)
                    misc_data = json.loads(video_info['misc_data'])
                    view_count = misc_data.get('viewCount', 0)
                    score = misc_data.get('relevance_score', 0)
                    print(f"   ✅ Found: {video_info['title'][:60]}... ({view_count} views, score: {score:.1f})")
                
                # Wait a bit between requests
                time.sleep(0.3)
            
            print(f"   📊 Found {len(videos)} unique videos for query: '{query}'")
            return videos
            
        except Exception as e:
            print(f"   ❌ Error during YouTube search: {e}")
            return []

def search_youtube(query, max_results=20):
    if not YOUTUBE_API_KEY:
        print("\n!!! YOUTUBE_API_KEY is missing. Cannot search YouTube. !!!")
        return []

    posts = []
    
    # Expand the search query to be more specific about the lightning event
    expanded_queries = [
        f"{query}",
        "NYC lightning June 26 2024",
        "New York lightning storm June 26 2024",        "Manhattan lightning June 2024",
        "One World Trade Center lightning 2024"
    ]
    
    try:
        # Initialize the YouTube collector
        collector = YouTubeCollector(YOUTUBE_API_KEY)
        
        # Track seen video IDs to avoid duplicates
        seen_videos = set()
        
        for expanded_query in expanded_queries:
            # Use the collector to search for videos with this query
            videos_for_query = collector.search_videos(expanded_query, max_results=max_results)
            
            # Add videos to our results, avoiding duplicates
            for video in videos_for_query:
                if video['id'] not in seen_videos:
                    seen_videos.add(video['id'])
                    posts.append(video)
                    
            # Wait between search queries to avoid quota issues
            if expanded_query != expanded_queries[-1]:
                time.sleep(0.5)

    except HttpError as e:
        print(f"\n--- YouTube API Error ---")
        print(f"An HTTP error occurred: {e}")
        if '403' in str(e):
            print("Hint: Your API key is invalid or your quota is exhausted.")
        print("-------------------------")
    except Exception as e:
        print(f"An unexpected error occurred in YouTube search: {e}")

    print(f"Found {len(posts)} relevant items on YouTube.")
      # Sort by relevance score and view count
    try:
        posts.sort(key=lambda x: (
            json.loads(x['misc_data']).get('relevance_score', 0),
            json.loads(x['misc_data']).get('viewCount', 0)
        ), reverse=True)
    except Exception as e:
        print(f"Error sorting videos: {e}")
        # Fall back to view count only
        try:        posts.sort(key=lambda x: json.loads(x['misc_data']).get('viewCount', 0), reverse=True)
        except Exception:
            pass
    
    print(f"Total YouTube videos found: {len(posts)}")
    # Return all results without limiting
    return posts


# --- YouTube Video Downloader Function ---
def download_youtube_videos(video_data, output_dir='data/raw/youtube'):
    """
    Download YouTube videos using yt-dlp.
    
    Args:
        video_data: List of dictionaries containing video metadata
        output_dir: Directory to save downloaded videos
        
    Returns:
        List of paths to downloaded videos
    """
    # Import required modules
    import subprocess
    
    # Check if yt-dlp is installed
    try:
        subprocess.run(['yt-dlp', '--version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      text=True, 
                      check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("yt-dlp is not installed. Please install it with: pip install yt-dlp")
        return []
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_paths = []
    
    print(f"\nDownloading {len(video_data)} YouTube videos to {output_dir}...")
    
    for i, video in enumerate(video_data):
        video_id = video['id']
        video_url = video['url']
        
        output_filename = f"{video_id}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        # Check if video already exists
        if os.path.exists(output_path):
            print(f"[{i+1}/{len(video_data)}] Video {video_id} already exists, skipping download")
            downloaded_paths.append(output_path)
            continue
            
        try:
            print(f"[{i+1}/{len(video_data)}] Downloading {video_url} with yt-dlp...")
            
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
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"Error downloading {video_url}: {stderr}")
                continue
            
            if os.path.exists(output_path):
                downloaded_paths.append(output_path)
                print(f"Successfully downloaded {video_url} to {output_path}")
            else:
                print(f"Download completed but file not found at {output_path}")
            
            # Wait a bit between downloads to avoid rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error downloading {video_url}: {e}")
    
    return downloaded_paths


# --- REDDIT COLLECTOR (Native API - PRAW) ---
def search_reddit(query, subreddits=None, max_results=20):
    if subreddits is None:
        subreddits = ['nyc', 'videos', 'newyork', 'lightning', 'weather', 'pics', 'photography', 'CityPorn', 'itookapicture']
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
        print("\n!!! Reddit PRAW keys are missing. Cannot search Reddit. !!!")
        return []
        
    print(f"Reddit API Keys loaded: Client ID: {REDDIT_CLIENT_ID[:5]}..., User Agent: {REDDIT_USER_AGENT}")
    posts = []
    
    # Initialize the Reddit API client
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        print(f"Successfully authenticated with Reddit API")
    except Exception as e:
        print(f"Error initializing PRAW: {e}")
        return []
    
    # Use a wider date range to improve chances of finding content (June 26 to July 15, 2024)
    # This captures posts about the event that were posted after it happened
    start_date_ts = datetime(2024, 6, 26, tzinfo=timezone.utc).timestamp()
    end_date_ts = datetime(2024, 7, 15, tzinfo=timezone.utc).timestamp()
    
    # Create expanded search queries
    search_queries = [
        query,
        "NYC lightning June 26",
        "Empire State Building lightning",
        "Manhattan lightning storm",
        "NYC thunderstorm June 26",
        "New York lightning strike",
    ]
    
    print(f"Searching Reddit for multiple queries in subreddits: {', '.join(subreddits)}")
    
    # Track processed submission IDs to avoid duplicates
    processed_ids = set()
    
    # Process each search query for each subreddit
    for search_query in search_queries:
        print(f"\nSearching with query: '{search_query}'")
        
        for subreddit_name in subreddits:
            if len(posts) >= max_results:
                break
                
            try:
                # PRAW search is limited to 100 results per request
                for submission in reddit.subreddit(subreddit_name).search(search_query, sort='relevance', limit=100):
                    # Skip if we've seen this submission before
                    if submission.id in processed_ids:
                        continue
                        
                    processed_ids.add(submission.id)
                    submission_time_ts = submission.created_utc
                    
                    # Client-side filtering by date
                    if start_date_ts <= submission_time_ts < end_date_ts:
                        # Check if this post is likely about the NYC lightning event
                        title_lower = submission.title.lower()
                        selftext_lower = submission.selftext.lower()
                        
                        # Look for keywords indicating relevance to NYC lightning
                        is_nyc = any(term in title_lower or term in selftext_lower 
                                    for term in ['nyc', 'new york', 'manhattan', 'brooklyn', 'empire state'])
                        is_lightning = any(term in title_lower or term in selftext_lower 
                                        for term in ['lightning', 'thunder', 'storm', 'strike'])
                        
                        # If it's about both NYC and lightning, or has high score, add it
                        if (is_nyc and is_lightning) or submission.score > 50:
                            submission_time = datetime.fromtimestamp(submission_time_ts, tz=timezone.utc)
                            
                            # Check if the URL points to an image or video
                            url = submission.url
                            is_media = any(url.endswith(ext) for ext in 
                                        ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm']) or 'i.redd.it' in url
                            
                            # Prioritize posts with media
                            if is_media or hasattr(submission, 'is_video') and submission.is_video:
                                posts.append({
                                    'platform': 'Reddit',
                                    'id': submission.id,
                                    'title': submission.title,
                                    'url': submission.url,
                                    'timestamp': submission_time.isoformat(),
                                    'misc_data': json.dumps({
                                        'selftext': submission.selftext, 
                                        'subreddit': subreddit_name, 
                                        'score': submission.score,
                                        'is_video': hasattr(submission, 'is_video') and submission.is_video,
                                        'search_query': search_query
                                    })
                                })
                                print(f"Found relevant Reddit post: {submission.title[:50]}... (score: {submission.score})")
                    
                    if len(posts) >= max_results:
                        break
                        
            except Exception as e:
                print(f"Error searching Reddit subreddit {subreddit_name} with query '{search_query}': {e}")
            
            # Pause between subreddit searches to avoid rate limiting
            time.sleep(0.5)
            
            if len(posts) >= max_results:
                break
    
    # Sort posts by score (highest first)
    try:
        posts.sort(key=lambda x: json.loads(x['misc_data']).get('score', 0), reverse=True)
    except Exception as e:
        print(f"Error sorting Reddit posts: {e}")
            
    print(f"Found {len(posts)} relevant items on Reddit.")
    return posts[:max_results]


# --- DATA COLLECTION WORKFLOW ---
def collect_data(query, max_results=20, append=False):
    """
    Collect data from multiple APIs and save to a CSV file.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return per platform
        append: Whether to append to existing CSV or overwrite
        
    Returns:
        DataFrame of collected data
    """
    print(f"\nCollecting data for query: '{query}'...")
    
    # Collect from YouTube
    youtube_data = search_youtube(query, max_results=max_results)
    print(f"Found {len(youtube_data)} items from YouTube")
    
    # Collect from Reddit 
    reddit_data = search_reddit(query, max_results=max_results)
    print(f"Found {len(reddit_data)} items from Reddit")
    
    # Combine data from all sources
    all_data = youtube_data + reddit_data
    
    if not all_data:
        print("No data collected from any source.")
        return pd.DataFrame()
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Create directory for metadata if it doesn't exist
    os.makedirs('data/metadata', exist_ok=True)
    
    # Save to CSV (append or overwrite)
    output_file = 'data/metadata/dataset_master.csv'
    
    # If append mode and file exists, read existing data and combine with new data
    if append and os.path.exists(output_file):
        try:
            existing_df = pd.read_csv(output_file)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            # Remove duplicates based on platform and id
            combined_df = combined_df.drop_duplicates(subset=['platform', 'id'])
            combined_df.to_csv(output_file, index=False)
            print(f"Appended new data - total {len(combined_df)} items in {output_file}")
            return combined_df
        except Exception as e:
            print(f"Error appending to CSV: {e}, will create new file")
            # Fall through to create new file
    
    # Save to CSV (new file or if append failed)
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} items to {output_file}")
    
    return df

def full_collection_workflow(query, max_results=20, download=True):
    """
    Run the full data collection workflow, including downloading videos.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return per platform
        download: Whether to download the videos
        
    Returns:
        DataFrame of collected data
    """
    # Use expanded queries like in collect_phase
    expanded_queries = [
        query,
        "lightning strike NYC Empire State Building June 26 2024",
        "NYC lightning storm video June 26",
        "Manhattan thunderstorm lightning footage June 2024",
        "Empire State Building hit by lightning June"
    ]
    
    all_results = []
    all_dataframes = []
    
    for expanded_query in expanded_queries:
        # Collect data with the individual query
        df = collect_data(expanded_query, max_results // len(expanded_queries))
        if not df.empty:
            all_dataframes.append(df)
        
        # Give the APIs a break between queries
        time.sleep(2)
    
    # Combine all results into one DataFrame and save
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Remove duplicates based on platform and id
        final_df = final_df.drop_duplicates(subset=['platform', 'id'])
        
        # Save the combined results
        output_file = 'data/metadata/dataset_master.csv'
        final_df.to_csv(output_file, index=False)
        print(f"Saved {len(final_df)} total unique items to {output_file}")
        
        # Download videos if requested
        if download and not final_df.empty:
            youtube_data = final_df[final_df['platform'] == 'YouTube'].to_dict('records')
            if youtube_data:
                download_youtube_videos(youtube_data)
        
        return final_df
    else:
        print("No data to process.")
        return pd.DataFrame()


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Example usage: collect YouTube and Reddit data, then download videos
    query = "lightning strike NYC June 26 2024"
    youtube_data = search_youtube(query, max_results=20)
    reddit_data = search_reddit(query, max_results=10)
    # Save combined metadata
    all_data = youtube_data + reddit_data
    df = pd.DataFrame(all_data)
    os.makedirs('data/metadata', exist_ok=True)
    df.to_csv('data/metadata/dataset_master.csv', index=False)
    print(f"Saved {len(all_data)} items to dataset_master.csv")
    # Download YouTube videos
    if youtube_data:
        download_youtube_videos(youtube_data)
