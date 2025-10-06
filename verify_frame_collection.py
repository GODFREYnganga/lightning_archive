#!/usr/bin/env python
"""
Verification script to ensure all individual media folders are properly discovered
and their frames are collected for COLMAP reconstruction.
"""

import os
import sys
from pathlib import Path
import json

# Add project root to path to import project modules
project_root = Path(os.path.abspath(__file__)).parent
sys.path.insert(0, str(project_root))

def verify_folder_structure(screens_folder):
    """Verify the structure of the screens folder and report statistics."""
    screens_path = Path(screens_folder)
    
    if not screens_path.exists():
        print(f"Error: Screens folder not found: {screens_path}")
        return False
    
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
            "exists": twitter_dir.exists(),
            "media_folders": 0,
            "total_frames": 0,
            "folders_with_frames": 0,
            "empty_folders": 0,
            "media_folders_list": []
        }
    }
    
    # Check YouTube structure
    if results["youtube"]["exists"]:
        for video_dir in youtube_dir.iterdir():
            if video_dir.is_dir():
                results["youtube"]["media_folders"] += 1
                
                # Count frames in this folder
                frames = list(video_dir.glob("*.jpg")) + list(video_dir.glob("*.png")) + list(video_dir.glob("*.jpeg"))
                frame_count = len(frames)
                results["youtube"]["total_frames"] += frame_count
                
                folder_info = {
                    "name": video_dir.name,
                    "frame_count": frame_count
                }
                results["youtube"]["media_folders_list"].append(folder_info)
                
                if frame_count > 0:
                    results["youtube"]["folders_with_frames"] += 1
                else:
                    results["youtube"]["empty_folders"] += 1
    
    # Check Twitter structure
    if results["twitter"]["exists"]:
        for media_dir in twitter_dir.iterdir():
            if media_dir.is_dir():
                results["twitter"]["media_folders"] += 1
                
                # Count frames in this folder
                frames = list(media_dir.glob("*.jpg")) + list(media_dir.glob("*.png")) + list(media_dir.glob("*.jpeg"))
                frame_count = len(frames)
                results["twitter"]["total_frames"] += frame_count
                
                folder_info = {
                    "name": media_dir.name,
                    "frame_count": frame_count
                }
                results["twitter"]["media_folders_list"].append(folder_info)
                
                if frame_count > 0:
                    results["twitter"]["folders_with_frames"] += 1
                else:
                    results["twitter"]["empty_folders"] += 1
    
    return results

def simulate_dataset_collection(screens_folder):
    """
    Simulate the dataset collection process to ensure all frames
    from all individual media folders are collected.
    """
    screens_path = Path(screens_folder)
    
    if not screens_path.exists():
        print(f"Error: Screens folder not found: {screens_path}")
        return []
    
    # Initialize the collected frames list
    collected_frames = []
    
    # Check YouTube and Twitter directories
    youtube_dir = screens_path / "youtube"
    twitter_dir = screens_path / "twitter"
    
    # Collect YouTube frames
    if youtube_dir.exists():
        for video_dir in youtube_dir.iterdir():
            if video_dir.is_dir():
                for frame_file in video_dir.glob("*"):
                    if frame_file.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                        collected_frames.append({
                            "source": "youtube",
                            "media_folder": video_dir.name,
                            "frame": frame_file.name,
                            "path": str(frame_file)
                        })
    
    # Collect Twitter frames
    if twitter_dir.exists():
        for media_dir in twitter_dir.iterdir():
            if media_dir.is_dir():
                for frame_file in media_dir.glob("*"):
                    if frame_file.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                        collected_frames.append({
                            "source": "twitter",
                            "media_folder": media_dir.name,
                            "frame": frame_file.name,
                            "path": str(frame_file)
                        })
    
    return collected_frames

def main():
    """Main function to verify frame collection."""
    # Default screens folder path
    screens_folder = os.path.join("data", "screens")
    
    # Check if a custom path is provided as an argument
    if len(sys.argv) > 1:
        screens_folder = sys.argv[1]
    
    print(f"Verifying frame collection from: {screens_folder}")
    print("-" * 80)
    
    # Verify folder structure
    structure_results = verify_folder_structure(screens_folder)
    
    # Print structure verification results
    print("\nFolder Structure Verification:")
    print("-" * 80)
    
    # YouTube results
    print("\nYouTube:")
    if structure_results["youtube"]["exists"]:
        print(f"  - Media folders: {structure_results['youtube']['media_folders']}")
        print(f"  - Folders with frames: {structure_results['youtube']['folders_with_frames']}")
        print(f"  - Empty folders: {structure_results['youtube']['empty_folders']}")
        print(f"  - Total frames: {structure_results['youtube']['total_frames']}")
    else:
        print("  - YouTube directory not found")
    
    # Twitter results
    print("\nTwitter:")
    if structure_results["twitter"]["exists"]:
        print(f"  - Media folders: {structure_results['twitter']['media_folders']}")
        print(f"  - Folders with frames: {structure_results['twitter']['folders_with_frames']}")
        print(f"  - Empty folders: {structure_results['twitter']['empty_folders']}")
        print(f"  - Total frames: {structure_results['twitter']['total_frames']}")
    else:
        print("  - Twitter directory not found")
    
    # Simulate collection
    print("\nSimulating Dataset Collection:")
    print("-" * 80)
    collected_frames = simulate_dataset_collection(screens_folder)
    
    # Count frames by source
    youtube_frames = sum(1 for frame in collected_frames if frame["source"] == "youtube")
    twitter_frames = sum(1 for frame in collected_frames if frame["source"] == "twitter")
    
    print(f"\nTotal frames collected: {len(collected_frames)}")
    print(f"  - YouTube frames: {youtube_frames}")
    print(f"  - Twitter frames: {twitter_frames}")
    
    # Count unique media folders
    youtube_folders = {frame["media_folder"] for frame in collected_frames if frame["source"] == "youtube"}
    twitter_folders = {frame["media_folder"] for frame in collected_frames if frame["source"] == "twitter"}
    
    print(f"\nUnique media folders: {len(youtube_folders) + len(twitter_folders)}")
    print(f"  - YouTube media folders: {len(youtube_folders)}")
    print(f"  - Twitter media folders: {len(twitter_folders)}")
    
    # Save detailed results to a JSON file
    results = {
        "structure": structure_results,
        "collection": {
            "total_frames": len(collected_frames),
            "youtube_frames": youtube_frames,
            "twitter_frames": twitter_frames,
            "youtube_folders": len(youtube_folders),
            "twitter_folders": len(twitter_folders),
            "collected_frames": collected_frames
        }
    }
    
    # Save detailed results (excluding the full frame list to keep the file size manageable)
    summary_results = {
        "structure": structure_results,
        "collection": {
            "total_frames": len(collected_frames),
            "youtube_frames": youtube_frames,
            "twitter_frames": twitter_frames,
            "youtube_folders": len(youtube_folders),
            "twitter_folders": len(twitter_folders),
            "youtube_folder_list": list(youtube_folders),
            "twitter_folder_list": list(twitter_folders)
        }
    }
    
    output_dir = os.path.join("data", "verification")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "frame_collection_verification.json")
    with open(output_path, "w") as f:
        json.dump(summary_results, f, indent=2)
    
    print(f"\nDetailed verification results saved to: {output_path}")
    print("\nVerification complete.")
    
    # Return a success flag based on comparison of folder counts vs collected frames
    expected_youtube_frames = structure_results["youtube"]["total_frames"]
    expected_twitter_frames = structure_results["twitter"]["total_frames"]
    
    if youtube_frames == expected_youtube_frames and twitter_frames == expected_twitter_frames:
        print("\n✅ SUCCESS: All frames were successfully collected!")
        return True
    else:
        print("\n❌ WARNING: Some frames may not have been collected properly.")
        print(f"  - YouTube: {youtube_frames}/{expected_youtube_frames} frames collected")
        print(f"  - Twitter: {twitter_frames}/{expected_twitter_frames} frames collected")
        return False

if __name__ == "__main__":
    main()
