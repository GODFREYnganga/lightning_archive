# Lightning Archive Technical Documentation

## Advanced Techniques for COLMAP-Ready Data Collection

This technical documentation outlines the key methodologies implemented in the Lightning Archive project to collect, process, and prepare lightning strike footage for 3D reconstruction using COLMAP.

## 1. API Integration & Data Collection

### 1.1 Multi-Platform API Handling

The Lightning Archive system implements robust API handling to collect data from multiple platforms:

#### YouTube Data API v3
```python
class YouTubeCollector:
    def __init__(self, api_key=None):
        self.api_key = api_key or YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.video_ids_seen = set()
    
    def search_videos(self, query, max_results=20):
        # Define temporal bounds for the lightning event
        published_after = "2024-06-26T00:00:00Z"
        published_before = "2024-06-28T23:59:59Z"
        
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'publishedAfter': published_after,
            'publishedBefore': published_before,
            'maxResults': min(max_results + 10, 50),
            'key': self.api_key,
            'order': 'relevance',
            'relevanceLanguage': 'en',
            'videoDuration': 'short'  # Prefer short videos
        }
        
        # Implementation includes error handling, rate limiting,
        # and metadata extraction from API responses
```

#### Reddit PRAW Integration
```python
def search_reddit(query, subreddits=None, max_results=20):
    # Initialize the Reddit API client
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    
    # Use expanded date range to capture content about the event
    start_date_ts = datetime(2024, 6, 26, tzinfo=timezone.utc).timestamp()
    end_date_ts = datetime(2024, 7, 15, tzinfo=timezone.utc).timestamp()
    
    # Content filtering example:
    is_nyc = any(term in title_lower or term in selftext_lower 
               for term in ['nyc', 'new york', 'manhattan', 'brooklyn', 'empire state'])
    is_lightning = any(term in title_lower or term in selftext_lower 
                     for term in ['lightning', 'thunder', 'storm', 'strike'])
```

### 1.2 API Request Optimization

The system employs several techniques to maximize API efficiency while respecting rate limits:

1. **Query Expansion:** Multiple related search terms are used to capture diverse content about the same event
   ```python
   expanded_queries = [
       query,
       "NYC lightning June 26 2024",
       "New York lightning storm June 26 2024",
       "Manhattan lightning June 2024",
       "One World Trade Center lightning 2024"
   ]
   ```

2. **Intelligent Rate Limiting:** Implementing delays between API calls to avoid rate limits
   ```python
   # Wait a bit between requests
   time.sleep(0.3)
   
   # Larger delay between search queries
   if expanded_query != expanded_queries[-1]:
       time.sleep(0.5)
   ```

3. **Duplicate Detection:** Tracking already seen IDs to avoid processing duplicates
   ```python
   # Skip if we've already seen this video
   if video_id in self.video_ids_seen:
       continue
   self.video_ids_seen.add(video_id)
   ```

4. **Error Recovery:** Comprehensive error handling with fallback mechanisms
   ```python
   try:
       # API call
   except HttpError as e:
       print(f"\n--- YouTube API Error ---")
       print(f"An HTTP error occurred: {e}")
       if '403' in str(e):
           print("Hint: Your API key is invalid or your quota is exhausted.")
   except Exception as e:
       print(f"An unexpected error occurred: {e}")
   ```

## 2. Media Processing & Frame Extraction

### 2.1 Organized Frame Extraction

The project implements an organized frame extraction system that:

1. Creates individual folders for each media file:
   ```python
   def process_youtube_video(video_path):
       video_name = video_path.stem
       # Create a subdirectory for each video to keep frames organized
       output_subdir = YOUTUBE_OUTPUT_DIR / video_name
   ```

2. Uses intelligent algorithms to select the most valuable frames:
   ```python
   def extract_frames_at_peak_brightness(video_path, output_folder, num_frames=5, min_frame_gap=15):
       # Calculate brightness values for all frames
       brightness_data = []
       while True:
           ret, frame = cap.read()
           if not ret:
               break
           # Calculate brightness (mean pixel value)
           brightness = np.mean(frame)
           brightness_data.append((frame_number, brightness))
           frame_number += 1
           
       # Sort by brightness (descending)
       brightness_data.sort(key=lambda x: x[1], reverse=True)
       
       # Get frames with highest brightness, ensuring min_frame_gap between them
       selected_frames = []
       for frame_number, brightness in brightness_data:
           # Check if this frame is far enough from already selected frames
           if all(abs(frame_number - selected) >= min_frame_gap_frames for selected in selected_frames):
               selected_frames.append(frame_number)
               if len(selected_frames) >= num_frames:
                   break
   ```

### 2.2 Deduplication via Image Hashing

The system uses perceptual hashing to detect and eliminate duplicate or near-duplicate images:

```python
def hash_image(image_path):
    """
    Generate a perceptual hash for an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        str: Perceptual hash string
    """
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Calculate perceptual hash using ImageHash library
        hash_obj = imagehash.phash(img)
        
        # Return hash as string
        return str(hash_obj)
    except Exception as e:
        print(f"Error calculating hash for {image_path}: {e}")
        return None

def are_similar_images(hash1, hash2, threshold=3):
    """
    Determine if two image hashes represent similar images.
    
    Args:
        hash1: First perceptual hash string
        hash2: Second perceptual hash string
        threshold: Maximum hamming distance for images to be considered similar
        
    Returns:
        bool: True if images are similar, False otherwise
    """
    # Convert hash strings to ImageHash objects
    if not hash1 or not hash2:
        return False
        
    h1 = imagehash.hex_to_hash(hash1)
    h2 = imagehash.hex_to_hash(hash2)
    
    # Calculate hamming distance between hashes
    distance = h1 - h2
    
    # Return True if distance is below threshold
    return distance <= threshold
```

This deduplication process is integrated into the dataset creation workflow:

```python
def _process_frame(self, frame_path, output_name, frame_index):
    # Calculate image hash for deduplication
    img_hash = hash_image(output_path)
    
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
```

## 3. Timestamp Synchronization

Accurate timestamp synchronization is crucial for temporal alignment of lightning strikes across multiple media sources.

### 3.1 Timestamp Extraction

```python
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
```

### 3.2 Temporal Proximity Analysis

The system selects frames with appropriate temporal spacing to avoid redundancy:

```python
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
```

### 3.3 Cross-Media Synchronization

The Lightning Archive implements cross-platform synchronization by:

1. Extracting creation timestamps from metadata
2. Using video frame timestamps to determine precise moments
3. Aligning frames from different sources based on visual similarity and timestamp proximity
4. Storing synchronized timestamps in the COLMAP metadata

```python
def synchronize_timestamps(metadata_df):
    """
    Synchronize timestamps across different media sources
    
    Args:
        metadata_df: DataFrame containing media metadata
        
    Returns:
        DataFrame with synchronized timestamps
    """
    # Group by platform to process each separately
    for platform, group in metadata_df.groupby('platform'):
        # Implementation details involve:
        # 1. Establishing a reference timestamp (t=0)
        # 2. Calculating offsets for each media source
        # 3. Adjusting timestamps relative to the reference
    
    return metadata_df
```

## 4. COLMAP Optimization & Reconstruction

### 4.1 Dataset Creation for COLMAP

```python
def create_dataset(self, max_frames=5, min_timestamp_proximity=0.5):
    """
    Create a dataset optimized for COLMAP
    """
    # Process all frames and collect metadata
    all_frames_metadata = []
    
    # Calculate vantage diversity
    vantage_diversity = self._calculate_vantage_diversity(all_frames_metadata)
    
    # Score each frame based on resolution, timestamp proximity, and vantage diversity
    scored_frames = []
    
    for frame in all_frames_metadata:
        resolution_score = self._get_image_resolution_score(frame['original_path'])
        
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
    # Selection process...
    
    # Generate COLMAP-friendly format
    colmap_data = {
        "dataset_name": "Lightning Strike NYC June 26 2024",
        "creation_date": datetime.now().isoformat(),
        "num_images": len(frames),
        "images": {}
    }
```

### 4.2 COLMAP Calibration & Feature Matching Tips

The Lightning Archive project has identified several key optimizations for COLMAP processing of lightning strike footage:

#### 4.2.1 Feature Extraction Optimization

```bash
# Recommended COLMAP feature extraction parameters for lightning
colmap feature_extractor \
    --database_path database.db \
    --image_path images \
    --ImageReader.camera_model SIMPLE_RADIAL \
    --SiftExtraction.use_gpu 1 \
    --SiftExtraction.max_num_features 8192 \
    --SiftExtraction.edge_threshold 10 \
    --SiftExtraction.peak_threshold 0.004 \
    --SiftExtraction.normalization true
```

**Key Optimizations:**
- Increased feature count (`max_num_features 8192`) to compensate for challenging lighting conditions
- Lower peak threshold (`peak_threshold 0.004`) to detect features in darker regions of the image
- Enabled normalization (`normalization true`) to handle extreme brightness variations

#### 4.2.2 Feature Matching Optimization

```bash
# Recommended COLMAP matching parameters for lightning
colmap exhaustive_matcher \
    --database_path database.db \
    --SiftMatching.use_gpu 1 \
    --ExhaustiveMatcher.block_size 50 \
    --ExhaustiveMatcher.lowes_ratio 0.8
```

**Key Optimizations:**
- Increased Lowe's ratio (`lowes_ratio 0.8`) to allow more matches in challenging conditions
- Using block-based matching to improve performance with larger image sets

#### 4.2.3 Mapping Optimization

```bash
# Recommended COLMAP mapper parameters for lightning
colmap mapper \
    --database_path database.db \
    --image_path images \
    --output_path sparse \
    --Mapper.ba_global_images_ratio 1.32 \
    --Mapper.ba_global_points_ratio 1.32 \
    --Mapper.filter_max_reproj_error 4 \
    --Mapper.init_min_num_inliers 15 \
    --Mapper.multiple_models 1 \
    --Mapper.extract_colors 1
```

**Key Optimizations:**
- Increased maximum reprojection error (`filter_max_reproj_error 4`) to accommodate lightning's visual uncertainty
- Reduced minimum inliers (`init_min_num_inliers 15`) for initial reconstruction
- Enabled multiple model support for disconnected sets of images

### 4.3 Verification of Frame Collection

The Lightning Archive implements a comprehensive verification system to ensure all frames are properly collected:

```python
def verify_folder_structure(screens_folder):
    """Verify the structure of the screens folder and report statistics."""
    # Check YouTube and Twitter directories
    youtube_dir = screens_path / "youtube"
    twitter_dir = screens_path / "twitter"
    
    results = {
        "youtube": {
            "exists": youtube_dir.exists(),
            "media_folders": 0,
            "total_frames": 0,
            "folders_with_frames": 0,
            "empty_folders": 0,
            "media_folders_list": []
        },
        "twitter": {
            # Similar structure
        }
    }
    
    # Check YouTube structure
    if results["youtube"]["exists"]:
        for video_dir in youtube_dir.iterdir():
            if video_dir.is_dir():
                results["youtube"]["media_folders"] += 1
                
                # Count frames in this folder
                frames = list(video_dir.glob("*.jpg")) + list(video_dir.glob("*.png"))
                frame_count = len(frames)
                results["youtube"]["total_frames"] += frame_count
```

## 5. Implementation Best Practices

### 5.1 Media Organization

The Lightning Archive uses a structured directory layout:

```
data/
  ├── metadata/
  │   └── dataset_master.csv
  ├── raw/
  │   ├── youtube/
  │   └── twitter/
  ├── screens/
  │   ├── youtube/
  │   │   ├── video1/
  │   │   │   ├── frame001.png
  │   │   │   ├── frame002.png
  │   │   └── video2/
  │   └── twitter/
  │       ├── media1/
  │       └── media2/
  ├── stills/
  │   └── colmap/
  │       ├── images/
  │       └── metadata/
  └── workflow_logs/
```

### 5.2 Logging & Reproducibility

The system implements comprehensive logging:

```python
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("data", "workflow_logs", "dataset_creation.log"), mode='a')
    ]
)
logger = logging.getLogger("dataset_creator")
```

### 5.3 Error Handling & Fallbacks

The all-in-one pipeline implements robust error handling and fallback mechanisms:

```powershell
try {
    # Run verification and dataset creation
    python verify_and_create_dataset.py
    if (-not $?) {
        Write-Host "Warning: Dataset creation completed with issues. Trying standard method..." -ForegroundColor Yellow
        $warningCount++
        
        # Try the standard method as fallback
        python -m lightning_archive --phase dataset
    }
} catch {
    Write-Host "Error in verification and dataset creation: $_" -ForegroundColor Red
    
    # Try the standard method as fallback
    Write-Host "Trying standard dataset creation as fallback..." -ForegroundColor Yellow
    try {
        python -m lightning_archive --phase dataset
    } catch {
        Write-Host "Error in standard dataset creation: $_" -ForegroundColor Red
        $errorCount++
    }
}
```

## 6. Extended References

For more details on specific components, see the following guides:

- **ORGANIZED_FRAMES_GUIDE.md**: Details on the frame organization system
- **FRAME_COLLECTION_VERIFICATION_GUIDE.md**: Documentation of the verification system
- **ENHANCED_SEARCH_GUIDE.md**: Information on the enhanced search functionality
- **TWITTER_COLLECTION_GUIDE.md**: Guide to Twitter data collection
- **YOUTUBE_DOWNLOAD_GUIDE.md**: Guide to YouTube video download process

---

This document outlines the key technical approaches used in the Lightning Archive project. These methods collectively enable the collection, processing, and preparation of lightning strike footage for high-quality 3D reconstruction using COLMAP.
