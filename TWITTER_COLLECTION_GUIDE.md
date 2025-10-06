# Twitter Media Collection

This guide explains how to use the Lightning Archive Twitter collection module to gather media related to the June 26, 2024 NYC lightning strike event.

## Prerequisites

1. **RapidAPI Key**: You'll need a RapidAPI key with access to the Twitter API45 endpoint.
2. **Python Environment**: Make sure you have Python installed with all the requirements.

## Setup

1. Create a `.env` file in the project root directory with your RapidAPI key:

```
RAPIDAPI_KEY=your_key_here
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Twitter Collector

### Option 1: Using the Run Scripts

The simplest way to collect Twitter data is to use the provided scripts:

- **Windows Command Prompt**: Run `run_twitter_collector.bat`
- **PowerShell**: Run `run_twitter_collector.ps1`

These scripts will:
1. Check for Python and the `.env` file
2. Run the Twitter collector with default parameters
3. Download media and generate metadata

### Option 2: Using the Module Directly

You can run the Twitter collector module directly with custom parameters:

```bash
python -m lightning_archive.twitter_collector --query "lightning strike NYC June 26" --max-results 30
```

#### Available Command-Line Options

| Option | Description |
|--------|-------------|
| `--query TEXT` | Base search query (default: "lightning strike NYC June 26 2024") |
| `--search-term TEXT` | Custom search term (if not specified, will be built from query) |
| `--date-range TEXT` | Date range in Twitter format (default: "since:2024-06-25 until:2024-06-28") |
| `--max-results INT` | Maximum number of results to return (default: 20) |
| `--no-save-csv` | Don't save results to CSV |
| `--api-only` | Only collect data from API, don't process media |
| `--process-only` | Only process existing data files, don't make API calls |
| `--file PATH` | Process a specific JSON file |
| `--integrate` | Run in integration mode compatible with api_collectors.py |

### Option 3: Integration with Full Pipeline

The Twitter collector integrates with the main Lightning Archive workflow:

```python
from lightning_archive.api_collectors import full_collection_workflow
from lightning_archive.twitter_collector import full_twitter_workflow

# Run just Twitter collection
twitter_data = full_twitter_workflow(
    query="lightning strike NYC June 26 2024",
    max_results=20
)

# Run full collection workflow (YouTube + Reddit + Twitter)
full_collection_workflow(
    query="lightning strike NYC June 26 2024",
    max_youtube_results=20, 
    max_reddit_results=10,
    include_twitter=True  # Set to True to include Twitter data
)
```

## Output Structure

The Twitter collector will generate:

1. **Raw API Data**: JSON files in `data/raw/twitter_api_responses/`
2. **Downloaded Media**: Images and videos in `data/raw/twitter/`
3. **Metadata**: CSV file in `data/metadata/twitter_media_metadata.csv`

## Media Scoring

Twitter media is automatically scored based on three factors:

1. **Resolution Score**: Higher resolution media receives a higher score
2. **Timestamp Proximity**: Media captured closer to the event time (June 26, 2024 at 10 PM EST) scores higher
3. **Vantage Diversity**: Media with location data scores higher, especially if from Manhattan

## Troubleshooting

- **No API Key**: If the RAPIDAPI_KEY is missing, the collector will try to process existing JSON files
- **API Rate Limits**: If you hit rate limits, try again later or reduce the number of requests
- **Permission Errors**: If you encounter permission errors when saving files, check folder permissions

## Advanced Usage

### Processing Existing Files

If you already have Twitter API response files:

```bash
python -m lightning_archive.twitter_collector --process-only
```

### API Data Collection Only

To only collect data from Twitter API without processing:

```bash
python -m lightning_archive.twitter_collector --api-only
```

### Processing a Specific File

```bash
python -m lightning_archive.twitter_collector --process-only --file "data/raw/twitter_api_responses/your_file.json"
```
