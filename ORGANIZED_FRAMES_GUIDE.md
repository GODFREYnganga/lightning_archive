# Organized Frame Extraction Guide

This guide explains how to use the organized frame extraction feature in Lightning Archive, which creates individual folders for each media file.

## Overview

The organized frame extraction feature processes each video or image from the raw media directories and creates a dedicated folder for each media file in the screens directory. This makes it easier to identify which frames came from which source media.

## Directory Structure

```
data/
│
├── raw/                     # Raw downloaded media 
│   ├── youtube/             # YouTube videos (mp4 files)
│   └── twitter/             # Twitter media (images and videos)
│
└── screens/                 # Extracted frames
    ├── youtube/             # Frames from YouTube videos
    │   ├── video1_id/       # Folder for video1
    │   │   ├── frame1.jpg
    │   │   ├── frame2.jpg
    │   │   └── ...
    │   │
    │   └── video2_id/       # Folder for video2
    │       ├── frame1.jpg
    │       └── ...
    │
    └── twitter/             # Frames from Twitter media
        ├── media1_id/       # Folder for media1
        │   └── frame.jpg
        └── media2_id/       # Folder for media2
            └── frame.jpg
```

## How to Use

### Using PowerShell Script

```powershell
# Run the PowerShell script
.\run_extract_frames_organized.ps1
```

### Using Batch File

```batch
# Run the batch file
run_extract_frames_organized.bat
```

### Running the Python Script Directly

```powershell
# Run the Python script directly
python extract_frames_organized.py
```

## How It Works

The script performs the following operations:

1. **Scans the Raw Media Directories**:
   - Locates all videos in `data/raw/youtube/`
   - Locates all media (videos and images) in `data/raw/twitter/`

2. **Creates Organized Output Structure**:
   - For each video or image, creates a dedicated subfolder named after the media file
   - Places all frames extracted from that media into its dedicated folder

3. **Processes Media Files**:
   - For videos: Extracts frames at peak brightness (likely lightning strikes)
   - For images: Processes and copies the image with standardized naming

## Advantages of Organized Folders

1. **Better Organization**: Each media file's frames are kept together
2. **Easier Tracking**: Quickly identify which frames came from which source
3. **Improved Analysis**: Compare frames from the same source together
4. **Simplifies COLMAP Processing**: Helps with grouping related frames

## Troubleshooting

- **No Folders Created**: Check that raw media exists in the expected locations
- **Empty Folders**: The script might not have found any suitable frames to extract
- **Media Format Issues**: Ensure media files are in supported formats
