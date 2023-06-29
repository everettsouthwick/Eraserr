import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("TAUTULLI_API_KEY")
BASE_URL = os.getenv("TAUTULLI_BASE_URL")

DAYS_THRESHOLD = 90  # Consider unplayed if added or last played more than this many days ago
FETCH_LIMIT = 5 # How many media items to fetch to process

def fetch_metadata(rating_key):
    params = {
        "apikey": API_KEY,
        "cmd": "get_metadata",
        "rating_key": rating_key
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code != 200:
        print(f"Metadata request for rating_key {rating_key} failed with status code {response.status_code}")
        return None, None
    
    metadata = response.json()

    if not metadata["response"]["data"]:
        return None, None
    
    item_id = None
    if 'guids' in metadata["response"]["data"]:
        for guid in metadata["response"]["data"]["guids"]:
            if "1" in metadata["response"]["data"]["section_id"]:
                if "tmdb://" in guid:
                    item_id = guid.replace("tmdb://", "")
                    break
            if "2" in metadata["response"]["data"]["section_id"]:
                if "tvdb://" in guid:
                    item_id = guid.replace("tvdb://", "")

    # Handle missing file_size in case of TV shows
    if "media_info" in metadata["response"]["data"] and metadata["response"]["data"]["media_info"]:
        file_size = int(metadata["response"]["data"]["media_info"][0]["parts"][0]["file_size"])
    else:
        file_size = 0  # Or handle it differently if needed

    return file_size, item_id

def fetch_season_and_episode_metadata(rating_key):
    total_size = 0

    # Get children metadata for TV shows
    params = {
        "apikey": API_KEY,
        "cmd": "get_children_metadata",
        "rating_key": rating_key
    }
    season_response = requests.get(BASE_URL, params=params)

    if season_response.status_code == 200:
        season_data = season_response.json()
        for season in season_data["response"]["data"]["children_list"]:
            params = {
                "apikey": API_KEY,
                "cmd": "get_children_metadata",
                "rating_key": season['rating_key']
            }
            episode_response = requests.get(BASE_URL, params=params)

            if episode_response.status_code == 200:
                episode_data = episode_response.json()
                for episode in episode_data["response"]["data"]["children_list"]:
                    file_size, tmdb_id = fetch_metadata(episode["rating_key"])
                    if file_size is not None and tmdb_id is not None:
                        total_size += file_size
    else:
        print(f"Fetching season/episode data failed with status code {season_response.status_code}")

    return total_size

def fetch_and_count_unplayed_titles(section_id):
    params = {
        "apikey": API_KEY,
        "cmd": "get_library_media_info",
        "section_id": section_id,
        "order_column": "last_played",
        "order_dir": "asc",
        "length": FETCH_LIMIT
    }
    response = requests.get(BASE_URL, params=params)

    count = 0
    total_size = 0
    item_ids = []
    threshold_timestamp = time.time() - DAYS_THRESHOLD * 24 * 60 * 60

    if response.status_code == 200:
        data = response.json()
        for item in data["response"]["data"]["data"]:
            rating_key = item["rating_key"]

            file_size, item_id = fetch_metadata(rating_key)
            if section_id == 2:
                file_size = fetch_season_and_episode_metadata(rating_key)

            if file_size is not None and item_id is not None:
                if item["last_played"] is None and int(item["added_at"]) < threshold_timestamp:
                    count += 1
                    total_size += file_size
                    item_ids.append(item_id)
                elif item["last_played"] is not None and int(item["last_played"]) < threshold_timestamp:
                    count += 1
                    total_size += file_size
                    item_ids.append(item_id)
            
            
    else:
        print(f"Request failed with status code {response.status_code}")

    total_size = convert_bytes(total_size)  # Convert total size to most suitable unit
    return count, total_size, item_ids

def convert_bytes(num):
    """
    This function will convert bytes to MB, GB, or TB
    """
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f"{num:3.1f} {unit}"
        num /= 1024.0