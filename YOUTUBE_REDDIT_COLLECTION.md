# Lightning Archive - YouTube & Reddit Collector

This tool collects videos and posts related to the lightning strike event in NYC on June 26, 2024, focusing on YouTube videos and Reddit posts.

## Setup

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your API keys:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   REDDIT_CLIENT_ID=your_reddit_client_id_here
   REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
   REDDIT_USER_AGENT=LightningArchiveBot/1.0 (by /u/your_username)
   ```

## Getting API Keys

### YouTube API Key
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the YouTube Data API v3
4. Create an API key
5. Add it to your `.env` file

### Reddit API Keys
1. Go to [Reddit's App Preferences](https://www.reddit.com/prefs/apps)
2. Create a new app (script)
3. Note the client ID and client secret
4. Add them to your `.env` file

## Usage

### Option 1: Run the Collection Scripts
The easiest way to run the collection is to use one of the provided scripts:

#### For Complete Collection (Search, Download, and Process):
- **Windows CMD**: Run `collect_youtube_data.bat` or `lightning_archive_all_in_one.bat`
- **PowerShell**: Run `.\collect_youtube_data.ps1` or `.\lightning_archive_all_in_one.ps1`

This will:
1. Search YouTube and Reddit for content related to the NYC lightning event
2. Download YouTube videos
3. Extract frames showing lightning strikes
4. Save all metadata and media files

#### For Search-Only (Metadata Collection without Downloads):
- **Windows CMD**: Run `search_only.bat`
- **PowerShell**: Run `.\search_only.ps1`

This will:
1. Search YouTube and Reddit for content related to the NYC lightning event
2. Save all metadata to CSV without downloading any media files

### Option 2: Run from Python

You can also run the collector from Python:

```python
from lightning_archive.api_collectors import full_collection_workflow

# Run with default settings
full_collection_workflow()

# Or customize parameters
full_collection_workflow(
    query="NYC lightning Empire State Building June 26 2024",
    max_youtube_results=15,
    max_reddit_results=10
)
```

## Output Files

The collection process creates the following outputs:

- **Metadata**: `data/metadata/dataset_master.csv`
- **Downloaded Videos**: `data/raw/youtube/`
- **Extracted Frames**: `data/screens/youtube/`

## Frame Extraction

The frame extraction process:
1. Analyzes each video frame-by-frame
2. Calculates a "lightning score" based on brightness patterns
3. Selects the frames most likely to show lightning strikes
4. Saves these frames as JPEG images

## Advanced Usage

### Search-Only Mode (Metadata Collection without Downloads)

You can run the search-only phase from the command line:
```bash
python -m lightning_archive --phase search_only --query "NYC lightning June 2024" --max-results 30
```

Or directly from Python code:
```python
from lightning_archive.api_collectors import full_collection_workflow

# Collect metadata without downloading videos
metadata_df = full_collection_workflow(
    query="NYC lightning June 2024", 
    max_results=30, 
    download=False
)
print(metadata_df)
```

For more details on search-only mode, see the `SEARCH_ONLY_GUIDE.md` file.

### Downloading Videos Only

```python
from lightning_archive.api_collectors import search_youtube, download_youtube_videos

# Search for videos
youtube_data = search_youtube("NYC lightning June 26 2024", max_results=10)

# Download just these videos
download_youtube_videos(youtube_data)
```

## Requirements

- Python 3.8+
- YouTube Data API v3 key
- Reddit API credentials
- `pytube` package (for downloading YouTube videos)
- OpenCV (for frame extraction)
- See `requirements.txt` for full dependencies

## License

This project is open source and available under the MIT License.
