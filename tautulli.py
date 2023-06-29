import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("TAUTULLI_API_KEY")
BASE_URL = os.getenv("TAUTULLI_BASE_URL")
DAYS_THRESHOLD = os.getenv("DAYS_THRESHOLD") # Consider unplayed if added or last played more than this many days ago
FETCH_LIMIT = os.getenv("TAUTULLI_FETCH_LIMIT") # How many media items to fetch to process

def fetch_metadata(rating_key):
    """
    This function fetches metadata for a given media item and returns its file size and item ID.

    Args:
        rating_key (int): The rating key of the media item to fetch metadata for.

    Returns:
        tuple: A tuple containing the file size of the media item and its item ID.
    """
    params = {
        "apikey": API_KEY,
        "cmd": "get_metadata",
        "rating_key": rating_key
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Metadata request for rating_key {rating_key} failed with status code {response.status_code}")
    
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
        file_size = 0

    return file_size, item_id

def fetch_season_and_episode_metadata(rating_key):
    """
    This function fetches metadata for all episodes in all seasons of a TV show.

    Args:
        rating_key (int): The rating key of the TV show to fetch metadata for.

    Returns:
        int: The total size of all episodes in all seasons of the TV show.
    """
    total_size = 0

    # Get children metadata for TV shows
    params = {
        "apikey": API_KEY,
        "cmd": "get_children_metadata",
        "rating_key": rating_key
    }
    season_response = requests.get(BASE_URL, params=params)

    if season_response.status_code != 200:
        raise Exception(f"Season metadata request for rating_key {rating_key} failed with status code {season_response.status_code}")
    
    season_data = season_response.json()
    for season in season_data["response"]["data"]["children_list"]:
        params = {
            "apikey": API_KEY,
            "cmd": "get_children_metadata",
            "rating_key": season['rating_key']
        }
        episode_response = requests.get(BASE_URL, params=params)

        if episode_response.status_code != 200:
            raise Exception(f"Episode metadata request for rating_key {season['rating_key']} failed with status code {episode_response.status_code}")
        
        episode_data = episode_response.json()
        for episode in episode_data["response"]["data"]["children_list"]:
            file_size, tmdb_id = fetch_metadata(episode["rating_key"])
            if file_size is not None and tmdb_id is not None:
                total_size += file_size

    return total_size

def fetch_and_count_unplayed_titles(section_id):
    """
    This function fetches metadata for unplayed media items in a given section of the Plex library and counts the number of unplayed titles.

    Args:
        section_id (int): The section ID of the Plex library to fetch metadata for.

    Returns:
        tuple: A tuple containing the count of unplayed titles, the total size of unplayed titles, and a list of item IDs for unplayed titles.
    """
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

    if response.status_code != 200:
        raise Exception(f"Library media info request for section_id {section_id} failed with status code {response.status_code}")
    
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