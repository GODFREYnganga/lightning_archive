# Frame Collection Verification for COLMAP Reconstruction

This document explains the enhanced frame collection process that ensures all frames from individual media folders are properly collected for COLMAP reconstruction.

## Overview

The Lightning Archive project now includes comprehensive verification to ensure that when processing frames for COLMAP reconstruction:

1. Each video/image from YouTube and Twitter has its own dedicated folder for extracted frames
2. The dataset creation phase properly collects frames from all individual media folders within both YouTube and Twitter screens directories

## Key Components

### Directory Structure

The standard directory structure for frames is:
```
data/
  screens/
    youtube/
      video1/
        frame1.jpg
        frame2.jpg
        ...
      video2/
        frame1.jpg
        ...
    twitter/
      media1/
        frame1.jpg
        ...
      media2/
        frame1.jpg
        ...
```

### Frame Collection Process

1. **Frame Extraction**: The frames are extracted using either `frames_extract.py` or `extract_frames_organized.py`. Both scripts create individual folders for each media file.

2. **Frame Collection**: The `dataset_creator.py` traverses both YouTube and Twitter directories, including all subdirectories, to find all available frames.

3. **Verification**: The new `verify_frame_collection.py` script ensures all frames in all individual media folders are discovered and collected properly.

## New Tools

### Verification Script

The `verify_frame_collection.py` script:
- Scans all media folders in YouTube and Twitter directories
- Counts frames in each folder
- Simulates the frame collection process
- Reports detailed statistics
- Validates that all frames are properly discovered

### Enhanced Dataset Creation

The `dataset_creator.py` has been enhanced with:
- Detailed logging of frames collected from each media folder
- Statistics on frame discovery and selection by source folder
- JSON reports showing frame collection performance

### All-in-One Verification and Dataset Creation

The `verify_and_create_dataset.py` script:
1. Verifies all frames from all media folders are properly discovered
2. Creates a COLMAP-ready dataset with the most suitable frames
3. Generates detailed logs and statistics

## Usage

### Run Verification Only

```
python verify_frame_collection.py [path/to/screens/folder]
```

### Verify and Create Dataset

```
python verify_and_create_dataset.py [--metadata PATH] [--screens PATH] [--output PATH] [--max-frames N]
```

### Using Batch/PowerShell Scripts

Windows CMD:
```
run_verify_and_create_dataset.bat
```

PowerShell:
```
.\run_verify_and_create_dataset.ps1
```

## Common Issues and Solutions

### Missing Frames

If verification shows missing frames:

1. Check that all media files have been properly processed with the frame extraction scripts
2. Ensure the screens directory contains properly organized YouTube and Twitter subdirectories
3. Verify permissions on the files and folders

### Empty Media Folders

If some media folders are empty:

1. Re-run the frame extraction process for those specific media files
2. Check if the original media files contain suitable lightning frames
3. Manually copy any frames that might be located in an incorrect folder

## Conclusion

With these enhancements, the Lightning Archive project ensures robust and comprehensive frame collection for COLMAP reconstruction, guaranteeing that all valuable frames from individual media sources are properly included in the final dataset.
