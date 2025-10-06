import pytest
from lightning_archive.api_collectors import collect_youtube_videos

def test_collect_youtube_videos():
    # This would require a mock or real API key
    # For now, assert structure
    videos = collect_youtube_videos("test", max_results=1)
    assert isinstance(videos, list)
