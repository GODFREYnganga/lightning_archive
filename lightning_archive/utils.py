import hashlib
import imagehash
from PIL import Image
from datetime import datetime

def hash_image(image_path):
    image = Image.open(image_path)
    return str(imagehash.average_hash(image))

def synchronize_timestamps(timestamps):
    # Assume timestamps are datetime objects, find median or something
    if not timestamps:
        return None
    sorted_ts = sorted(timestamps)
    return sorted_ts[len(sorted_ts)//2]

def parse_timestamp(ts_str):
    # Parse various formats
    try:
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except:
        return datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
