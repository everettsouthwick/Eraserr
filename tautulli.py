from dotenv import load_dotenv
import requests
import time
import os

load_dotenv()

API_KEY = os.getenv("TAUTULLI_API_KEY")
BASE_URL = os.getenv("TAUTULLI_BASE_URL")

DEFAULT_DAYS_THRESHOLD = 30
DEFAULT_FETCH_LIMIT = '25'
DAYS_THRESHOLD = int(os.getenv("DAYS_THRESHOLD", DEFAULT_DAYS_THRESHOLD)) # How many days to wait before deleting unplayed media
FETCH_LIMIT = os.getenv("TAUTULLI_FETCH_LIMIT", DEFAULT_FETCH_LIMIT) # How many items to fetch at a time

def fetch_libraries(section_type):
    params = {
        "apikey": API_KEY,
        "cmd": "get_libraries"
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"Fetching libraries failed with status code {response.status_code}")
    
    libraries = response.json()

    if not libraries["response"]["data"]:
        return None

    section_ids = [library["section_id"] for library in libraries["response"]["data"] 
                   if library["section_type"] == section_type]
    return section_ids
        

def fetch_metadata(rating_key):
    """
    Fetches metadata for a given rating key.

    Args:
        rating_key (str): The rating key for the media item.

    Returns:
        str: The item ID for the media item, or None if it could not be found.
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
        return None
    
    item_id = None
    for guid in metadata["response"]["data"]["guids"]:
        if "movie" in metadata["response"]["data"]["media_type"]:
            if "tmdb://" in guid:
                item_id = guid.replace("tmdb://", "")
                break
        elif "show" in metadata["response"]["data"]["media_type"]:
            if "tvdb://" in guid:
                item_id = guid.replace("tvdb://", "")
                break

    return item_id

def fetch_and_count_unplayed_titles(section_id):
    """
    Fetches the unplayed titles for a given section ID and counts them.

    Args:
        section_id (int): The section ID to fetch unplayed titles for.

    Returns:
        tuple: A tuple containing the count of unplayed titles and a list of their item IDs.
    """
    count = 0
    item_ids = []
    threshold_timestamp = time.time() - DAYS_THRESHOLD * 24 * 60 * 60
    start = 0
    max_executions_allowed = 1000
    
    while True and max_executions_allowed > 0:
        params = {
            "apikey": API_KEY,
            "cmd": "get_library_media_info",
            "section_id": section_id,
            "order_column": "last_played",
            "order_dir": "asc",
            "length": FETCH_LIMIT,
            "start": start
        }
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Library media info request for section_id {section_id} failed with status code {response.status_code}")

        data = response.json()
        
        # Break loop if no more data
        if not data["response"]["data"]["data"]:
            break
        
        for item in data["response"]["data"]["data"]:
            rating_key = item["rating_key"]

            item_id = fetch_metadata(rating_key)

            if item_id is not None:
                if item["last_played"] is None and int(item["added_at"]) < threshold_timestamp:
                    count += 1
                    item_ids.append(item_id)
                elif item["last_played"] is not None and int(item["last_played"]) < threshold_timestamp:
                    count += 1
                    item_ids.append(item_id)
        
        # Increment the 'start' parameter for the next iteration
        start += FETCH_LIMIT
        max_executions_allowed -= 1

    return count, item_ids


