@echo off
echo ===== LIGHTNING ARCHIVE COMPLETE PIPELINE =====

echo 1. Running search and collection phase...
python -m lightning_archive --phase collect

echo Running Twitter collection (if you have Twitter API keys)...
call run_twitter_collector.bat

echo 2. Running download phase...
python -m lightning_archive --phase download

echo 3. Running frame extraction phase...
python -m lightning_archive --phase extract

echo 4. Running dataset creation phase...
python -m lightning_archive --phase dataset

echo Complete pipeline execution finished!
