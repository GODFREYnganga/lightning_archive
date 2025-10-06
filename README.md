# Lightning Archive

A Python tool for archiving social media data related to lightning strikes, optimized for 3D reconstruction using COLMAP.

## Project Overview

The Lightning Archive project collects videos and photos from social media platforms like YouTube and Twitter/X that capture lightning strikes, with a specific focus on the June 26, 2024 NYC thunderstorm. The collected media is processed for 3D reconstruction using COLMAP (Structure-from-Motion and Multi-View Stereo).

### Key Features

- **Multi-Platform Collection**: Gathers media from YouTube and Twitter/X
- **Metadata Management**: Tracks source information and temporal alignment
- **Frame Extraction**: Processes videos into synchronized still frames
- **Organized Media Structure**: Each video/image has its own dedicated folder for extracted frames
- **Frame Collection Verification**: Ensures all individual media folders are properly processed
- **3D Reconstruction Preparation**: Organizes data for COLMAP processing

## Installation

### Prerequisites

- Python 3.8 or higher
- API keys for data collection:
  - `YOUTUBE_API_KEY`: For accessing YouTube API
  - `TWITTER_BEARER_TOKEN`: For accessing Twitter/X API

### Quick Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Lightning_archive.git
   cd Lightning_archive
   ```

2. Install using the provided scripts:
   - Windows:
     ```bash
     .\install_dependencies.bat
     ```
   - PowerShell:
     ```bash
     .\install_dependencies.ps1
     ```
   - Linux/macOS:
     ```bash
     pip install -r requirements.txt
     pip install -e .
     ```

### Manual Installation

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

3. For development, install additional requirements:
   ```bash
   pip install -r dev-requirements.txt
   ```

## Project Structure

```
Lightning_archive/
├── lightning_archive/         # Main package
│   ├── __main__.py            # Entry point
│   ├── api_collectors.py      # API collection functionality (incl. yt-dlp downloads)
│   ├── dataset_creator.py     # Dataset creation tools
│   ├── download_manager.py    # Unified media downloader
│   ├── frame_extractor.py     # Video frame extraction
│   ├── frames_extract.py      # Frame processing utilities
│   ├── metadata_manager.py    # Metadata handling
│   ├── twitter_collector.py   # Twitter/X specific collection
│   └── utils.py               # Utility functions
├── data/                      # Data directory (created at runtime)
│   ├── raw/                   # Raw collected media
│   ├── stills/                # Extracted video frames
│   ├── screens/               # Screenshots and previews
│   └── metadata/              # CSV and JSON metadata
├── tests/                     # Test modules
├── install_dependencies.bat   # Windows installation script
├── install_dependencies.ps1   # PowerShell installation script
├── requirements.txt           # Dependencies
└── pyproject.toml             # Package configuration
```

## Usage

### Command Line Interface

Run the main module with options:
```bash
python -m lightning_archive [COMMAND] [OPTIONS]
```

Run the tool using the `--phase` argument:
```bash
python -m lightning_archive --phase [PHASE] [OPTIONS]
```

Available phases:
- `search_only`: Search and collect metadata only (no downloads)
- `collect`: Collect data from APIs and prepare for downloads
- `download`: Download media from metadata
- `extract`: Extract frames from videos
- `dataset`: Create a dataset for COLMAP
- `all`: Run the complete workflow (default)

### Workflow Examples

#### 1. Complete Data Collection and Processing

```bash
# Collect media metadata, download files, and extract frames
python -m lightning_archive --phase all
```

#### 2. Search Only (No Downloads)

```bash
# Search and collect metadata only from APIs (no downloads)
python -m lightning_archive --phase search_only
```

#### 3. Collect Metadata and Prepare for Downloads

```bash
# Collect metadata and prepare for downloads
python -m lightning_archive --phase collect
```

#### 4. Download Media from Metadata

```bash
# Download media files based on collected metadata
python -m lightning_archive --phase download
```

#### 5. Extract Frames from Videos

```bash
# Extract frames from downloaded videos
python -m lightning_archive --phase extract
```

#### 6. Extract Frames with Organized Folders

```bash
# Extract frames into organized folders (one folder per media file)
.\run_extract_frames_organized.ps1
```

### Direct Scripts

We provide several direct script alternatives that bypass module imports for more reliable execution:

#### YouTube Downloads with yt-dlp

```bash
# Run direct YouTube download with yt-dlp
python download_youtube_direct.py
```

#### Frame Extraction

```bash
# Extract frames directly from downloaded videos 
python extract_frames_direct.py

# Extract frames into organized folders (one folder per media)
python extract_frames_organized.py
```

The project now uses yt-dlp instead of pytube for more reliable YouTube downloads across all components.

For scenarios where the main module import system is experiencing issues, we've created direct scripts that bypass the module import system:

#### Direct YouTube Download

```bash
# Windows Batch
.\run_youtube_download_direct.bat

# PowerShell
.\run_youtube_download_direct.ps1
```

#### Direct Frame Extraction

```bash
# Windows Batch
.\run_extract_frames_direct.bat

# PowerShell
.\run_extract_frames_direct.ps1
```

#### 6. Create Dataset for COLMAP

```bash
# Create a dataset ready for COLMAP processing
python -m lightning_archive --phase dataset
```

#### 7. Verify and Create Dataset for COLMAP

```bash
# Verify frame collection and create a dataset for COLMAP
python verify_and_create_dataset.py

# Windows Batch
.\run_verify_and_create_dataset.bat

# PowerShell
.\run_verify_and_create_dataset.ps1
```

The verification ensures all frames from individual media folders are properly collected for the COLMAP dataset.

## Documentation

We provide several guides to help you use the Lightning Archive effectively:

- **[ORGANIZED_FRAMES_GUIDE.md](ORGANIZED_FRAMES_GUIDE.md)**: Guide to organizing frames by media source
- **[FRAME_COLLECTION_VERIFICATION_GUIDE.md](FRAME_COLLECTION_VERIFICATION_GUIDE.md)**: Guide to verifying frame collection for COLMAP
- **[ENHANCED_SEARCH_GUIDE.md](ENHANCED_SEARCH_GUIDE.md)**: Guide to enhanced search functionality
- **[SEARCH_ONLY_GUIDE.md](SEARCH_ONLY_GUIDE.md)**: Guide to search-only functionality
- **[TWITTER_COLLECTION_GUIDE.md](TWITTER_COLLECTION_GUIDE.md)**: Guide to Twitter data collection
- **[YOUTUBE_DOWNLOAD_GUIDE.md](YOUTUBE_DOWNLOAD_GUIDE.md)**: Guide to YouTube video download

## Data Structure

The project automatically creates the following directories:

- `/data/raw/`: Raw downloaded media files
  - `/youtube/`: YouTube videos
  - `/twitter/`: Twitter/X media files
- `/data/stills/`: Extracted and synchronized video frames
  - `/colmap/images/`: Prepared images for COLMAP
  - `/colmap/metadata/`: COLMAP-related metadata
- `/data/metadata/`: Metadata files including timestamps and sources
  - `dataset_master.csv`: Master dataset metadata
- `/data/screens/`: Thumbnails and preview images
- `/data/workflow_logs/`: Logs from the collection and processing workflows

## Notes for COLMAP Use

- For optimal 3D reconstruction, use extracted stills with overlapping views
- Adjust timestamp offsets in the metadata for proper temporal alignment
- Use the master CSV to filter frames by timestamp for synchronized views
- Consider the camera parameters in the metadata for better reconstruction

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.
