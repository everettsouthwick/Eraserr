from util import convert_bytes
from dotenv import load_dotenv
import requests
import os

load_dotenv()

API_KEY = os.getenv("RADARR_API_KEY")
BASE_URL = os.getenv("RADARR_BASE_URL")
EXEMPT_TAG_NAME = os.getenv("RADARR_EXEMPT_TAG_NAME")

DRY_RUN = os.getenv("DRY_RUN", "False").lower() in ("true", "1", "t")


def get_radarr_tag_id(tag_name):
    """
    Retrieves the Radarr tag ID given its name.

    Args:
        tag_name (str): The name of the tag.

    Returns:
        int: The ID of the tag.

    Raises:
        requests.exceptions.RequestException: If the request to retrieve the Radarr tag ID fails.
    """
    url = f"{BASE_URL}/tag"
    headers = {"X-Api-Key": API_KEY}

    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        tags = response.json()
        for tag in tags:
            if tag["label"] == tag_name:
                return tag["id"]
        return None
    raise requests.exceptions.RequestException(f"Fetching Radarr tag ID failed with status code {response.status_code}")


def get_radarr_id(tmdb_id):
    """
    Retrieves the Radarr ID, title, and size on disk of a movie given its TMDB ID.

    Args:
        tmdb_id (int): The TMDB ID of the movie.

    Returns:
        Tuple[int, str, int, int[]]: A tuple containing the Radarr ID, title, size on disk and tags of the movie.

    Raises:
        requests.exceptions.RequestException: If the request to retrieve the Radarr ID fails.
    """
    url = f"{BASE_URL}/movie"
    headers = {"X-Api-Key": API_KEY}
    params = {"tmdbId": tmdb_id}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    if response.status_code == 200:
        movie_data = response.json()
        if not movie_data:
            return None, None, None, None
        return movie_data[0]["id"], movie_data[0]["title"], movie_data[0]["sizeOnDisk"], movie_data[0]["tags"]

    raise requests.exceptions.RequestException(f"Fetching Radarr ID failed with status code {response.status_code}")


def find_and_delete_movie(tmdb_id):
    """
    Finds a movie in Radarr given its TMDB ID and deletes it if it has not been played.

    Args:
        tmdb_id (int): The TMDB ID of the movie.

    Returns:
        Tuple[boolean, int]: A tuple containing whether the movie was deleted and the size of the movie that was deleted in bytes.

    Raises:
        requests.exceptions.RequestException: If the request to retrieve the Radarr ID fails or if the deletion fails.
    """
    exempt_tag_id = get_radarr_tag_id(EXEMPT_TAG_NAME)
    radarr_id, title, size_on_disk, tags = get_radarr_id(tmdb_id)
    if radarr_id is None or title is None:
        raise requests.exceptions.RequestException(f"Fetching Radarr ID failed")

    if exempt_tag_id is not None and tags is not None and exempt_tag_id in tags:
        print(f"RADARR :: {title} is exempt from deletion")
        return False, 0

    deleted = delete_unplayed_movie(radarr_id, title, size_on_disk)

    return deleted, size_on_disk


def delete_unplayed_movie(radarr_id, title, size_on_disk):
    """
    Deletes a movie in Radarr given its ID, title, and size on disk if it has not been played.

    Args:
        radarr_id (int): The ID of the movie in Radarr.
        title (str): The title of the movie.
        size_on_disk (int): The size of the movie on disk in bytes.

    Returns:
        boolean: Whether the movie was deleted.

    Raises:
        requests.exceptions.RequestException: If the deletion fails.
    """
    url = f"{BASE_URL}/movie/{radarr_id}"
    headers = {"X-Api-Key": API_KEY}
    params = {"deleteFiles": "true"}

    if DRY_RUN:
        print(f"RADARR :: DRY RUN :: Would have deleted {title} and freed up {convert_bytes(size_on_disk)}")
        return True

    response = requests.delete(url, headers=headers, params=params, timeout=30)
    if response.status_code == 200:
        print(f"RADARR :: {title} deleted successfully. {convert_bytes(size_on_disk)} freed up")
        return True

    raise requests.exceptions.RequestException(f"Deletion failed with status code {response.status_code}")
