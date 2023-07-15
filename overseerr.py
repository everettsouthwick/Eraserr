import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OVERSEERR_API_KEY")
BASE_URL = os.getenv("OVERSEERR_BASE_URL")

DRY_RUN = os.getenv("DRY_RUN", "False").lower() in ("true", "1", "t")
DEFAULT_FETCH_LIMIT = "10"
FETCH_LIMIT = int(os.getenv("OVERSEERR_FETCH_LIMIT", DEFAULT_FETCH_LIMIT))


def fetch_overseerr_media():
    """
    Fetches a list of media from the Overseerr API.

    Returns:
        A list of media objects.
    Raises:
        Exception: If the API request fails.
    """
    url = f"{BASE_URL}/media"
    headers = {"X-API-KEY": API_KEY}

    media_list = []
    skip = 0
    max_executions_allowed = 1000

    while True and max_executions_allowed > 0:
        params = {
            "take": FETCH_LIMIT,
            "skip": skip,
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Fetching Overseerr media failed with status code {response.status_code}")

        request_data = response.json()

        # Break loop if no more data
        if not request_data["results"]:
            break

        media_list.extend(request_data["results"])

        # Increment the 'page' parameter for the next iteration
        skip += FETCH_LIMIT
        max_executions_allowed -= 1

    return media_list


def find_and_delete_media(item_id):
    """
    Finds and deletes media with the given item ID from the Overseerr API.

    Args:
        item_id: The ID of the item to delete.

    Returns:
        None
    """
    media = fetch_overseerr_media()
    if media is None:
        return

    for item in media:
        if item["mediaType"] is None:
            continue

        if item["mediaType"] == "movie" and item["tmdbId"] == int(item_id):
            delete_media(item["id"])
            break
        elif item["mediaType"] == "tv" and item["tvdbId"] == int(item_id):
            delete_media(item["id"])
            break


def delete_media(media_id):
    """
    Deletes media with the given ID from the Overseerr API.

    Args:
        media_id (int): The ID of the media to delete.

    Returns:
        None

    Raises:
        Exception: If the API request fails.
    """
    url = f"{BASE_URL}/media/{media_id}"
    headers = {"X-API-KEY": API_KEY}

    if DRY_RUN:
        print(f"OVERSEERR :: DRY RUN :: Would have deleted media {media_id}")
        return

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"OVERSEERR :: Media {media_id} deleted successfully.")
    else:
        raise Exception(f"Deletion of media {media_id} failed with status code {response.status_code}")
