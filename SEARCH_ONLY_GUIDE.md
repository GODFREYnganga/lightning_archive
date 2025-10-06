# Search-Only Mode Guide

## Overview

The search-only mode is designed to allow you to search for and collect metadata about lightning strike videos and images without actually downloading the media files. This is useful for:

1. **Preview Data Collection**: Check what media is available before committing to downloads
2. **Metadata Analysis**: Analyze the available content, timestamps, and relevance scores
3. **Bandwidth Conservation**: Useful in situations where you have limited bandwidth
4. **Storage Efficiency**: Helpful when you want to evaluate available data without using storage space

## How Search-Only Mode Works

When you run Lightning Archive in search-only mode, the system will:

1. Search YouTube and Reddit APIs for content matching your query
2. Process and score the results for relevance to lightning strikes
3. Save all metadata to the master CSV file
4. Skip the media download, frame extraction, and dataset creation phases

## Using Search-Only Mode

### Command Line Usage

```bash
python -m lightning_archive --phase search_only --query "lightning strike NYC June 26 2024" --max-results 20
```

### Using Provided Scripts

For convenience, we've included two scripts:

- Windows Batch file: `search_only.bat`
- PowerShell script: `search_only.ps1`

Simply run the appropriate script for your system, and it will execute the search-only workflow with default parameters.

## Output

The search-only mode produces the following output:

- `data/metadata/dataset_master.csv`: Master metadata file containing all found media information
- Console output with relevance scores and search statistics

## Next Steps After Search-Only Mode

After running search-only mode, you can:

1. **Review the metadata**: Open the CSV file to see what content was found
2. **Filter results**: Use tools like Excel or Python to filter the results based on relevance scores
3. **Proceed to download**: If satisfied with the results, run the download phase:
   ```bash
   python -m lightning_archive --phase download
   ```

## Example Workflow

1. Run search-only mode to find available content:
   ```bash
   python -m lightning_archive --phase search_only
   ```

2. Review the metadata in `data/metadata/dataset_master.csv`

3. If satisfied with the results, download the media:
   ```bash
   python -m lightning_archive --phase download
   ```

4. Continue with frame extraction and dataset creation:
   ```bash
   python -m lightning_archive --phase extract
   python -m lightning_archive --phase dataset
   ```

This phased approach gives you more control over the data collection process while preserving bandwidth and storage space until you're ready to process the full dataset.
