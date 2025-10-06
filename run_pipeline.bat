@echo off
echo Lightning Archive Data Collection Pipeline
echo ========================================

echo Step 1: Collect metadata from APIs
python -m lightning_archive

echo.
echo Step 2: Download media from collected sources
python -c "from lightning_archive.media_downloader import download_all_media_from_metadata; download_all_media_from_metadata('data/metadata/dataset_master.csv', 'data/raw')"

echo.
echo Step 3: Extract frames from videos
python -c "import os; from lightning_archive.__main__ import extract_phase; extract_phase()"

echo.
echo Step 4: Create dataset for COLMAP
python -c "from lightning_archive.dataset_creator import DatasetCreator; creator = DatasetCreator('data/metadata/dataset_master.csv', 'data/stills', 'data/colmap_dataset'); creator.create_dataset(max_frames=5)"

echo.
echo Pipeline complete!
