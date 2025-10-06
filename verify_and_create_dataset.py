#!/usr/bin/env python
"""
Script to verify and create a COLMAP-ready dataset, ensuring frames 
from all individual media folders are properly collected.
"""

import os
import sys
from pathlib import Path
import argparse
import time
from datetime import datetime

# Add project root to path to import project modules
project_root = Path(os.path.abspath(__file__)).parent
sys.path.insert(0, str(project_root))

from lightning_archive.dataset_creator1 import DatasetCreator
from verify_frame_collection import verify_folder_structure, simulate_dataset_collection

def main():
    """Main function to verify frame collection and create dataset."""
    parser = argparse.ArgumentParser(description="Verify and create COLMAP-ready dataset.")
    parser.add_argument("--metadata", default="data/metadata/dataset_master.csv", 
                        help="Path to metadata CSV file")
    parser.add_argument("--screens", default="data/screens", 
                        help="Path to screens folder containing extracted frames")
    parser.add_argument("--output", default=None, 
                        help="Output folder for the processed dataset (default: data/stills)")
    parser.add_argument("--max-frames", type=int, default=5,
                        help="Maximum number of frames to include in the dataset (default: 5)")
    parser.add_argument("--verify-only", action="store_true",
                        help="Only verify frame collection without creating dataset")
    parser.add_argument("--skip-verify", action="store_true",
                        help="Skip verification and proceed directly to dataset creation")
    args = parser.parse_args()
    
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"Lightning Archive Dataset Verification and Creation")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    # Ensure output directory exists for logs
    log_dir = os.path.join("data", "workflow_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Step 1: Verify frame collection
    if not args.skip_verify:
        print("\nStep 1: Verifying Frame Collection")
        print("-" * 80)
        
        structure_results = verify_folder_structure(args.screens)
        collected_frames = simulate_dataset_collection(args.screens)
        
        # Count frames by source
        youtube_frames = sum(1 for frame in collected_frames if frame["source"] == "youtube")
        twitter_frames = sum(1 for frame in collected_frames if frame["source"] == "twitter")
        
        print(f"\nVerification Summary:")
        print(f"- YouTube: {youtube_frames} frames from {structure_results['youtube']['media_folders']} folders")
        print(f"- Twitter: {twitter_frames} frames from {structure_results['twitter']['media_folders']} folders")
        
        # Check if verification failed
        expected_youtube_frames = structure_results["youtube"]["total_frames"]
        expected_twitter_frames = structure_results["twitter"]["total_frames"]
        
        if (youtube_frames != expected_youtube_frames or 
            twitter_frames != expected_twitter_frames):
            print("\n⚠️ Warning: Frame collection verification detected issues!")
            print(f"- YouTube: {youtube_frames}/{expected_youtube_frames} frames collected")
            print(f"- Twitter: {twitter_frames}/{expected_twitter_frames} frames collected")
            
            if not input("\nContinue with dataset creation anyway? (y/N): ").lower().startswith('y'):
                print("Dataset creation aborted.")
                return
    
    if args.verify_only:
        print("\nVerification complete. Skipping dataset creation as requested.")
        return
    
    # Step 2: Create COLMAP-ready dataset
    print("\nStep 2: Creating COLMAP-Ready Dataset")
    print("-" * 80)
    
    # Create dataset
    creator = DatasetCreator(args.metadata, args.screens, args.output)
    output_dir = creator.create_dataset(max_frames=args.max_frames)
    
    if output_dir:
        print(f"\n✅ Dataset created successfully in: {output_dir}")
    else:
        print(f"\n❌ Failed to create dataset")
    
    print(f"\nProcess completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
