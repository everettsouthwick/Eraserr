from util import convert_bytes
from dotenv import load_dotenv
import requests
import os

load_dotenv()

API_KEY = os.getenv("RADARR_API_KEY")
BASE_URL = os.getenv("RADARR_BASE_URL")

DRY_RUN = os.getenv("DRY_RUN", "False").lower() in ("true", "1", "t")


def get_radarr_id(tmdb_id):
    """
    Retrieves the Radarr ID, title, and size on disk of a movie given its TMDB ID.

    Args:
        tmdb_id (int): The TMDB ID of the movie.

    Returns:
        Tuple[int, str, int]: A tuple containing the Radarr ID, title, and size on disk of the movie.

    Raises:
        Exception: If the request to retrieve the Radarr ID fails.
    """
    url = f"{BASE_URL}/movie"
    headers = {"X-Api-Key": API_KEY}
    params = {"tmdbId": tmdb_id}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        movie_data = response.json()
        if not movie_data:
            return None, None, None
        return movie_data[0]["id"], movie_data[0]["title"], movie_data[0]["sizeOnDisk"]
    else:
        raise Exception(f"Fetching Radarr ID failed with status code {response.status_code}")


def find_and_delete_movie(tmdb_id):
    """
    Finds a movie in Radarr given its TMDB ID and deletes it if it has not been played.

    Args:
        tmdb_id (int): The TMDB ID of the movie.

    Returns:
        int: The size of the movie that was deleted in bytes.

    Raises:
        Exception: If the request to retrieve the Radarr ID fails or if the deletion fails.
    """
    radarr_id, title, size_on_disk = get_radarr_id(tmdb_id)
    if radarr_id is None or title is None:
        raise Exception(f"Fetching Radarr ID failed")

    delete_unplayed_movie(radarr_id, title, size_on_disk)

    return size_on_disk


def delete_unplayed_movie(radarr_id, title, size_on_disk):
    """
    Deletes a movie in Radarr given its ID, title, and size on disk if it has not been played.

    Args:
        radarr_id (int): The ID of the movie in Radarr.
        title (str): The title of the movie.
        size_on_disk (int): The size of the movie on disk in bytes.

    Raises:
        Exception: If the deletion fails.
    """
    url = f"{BASE_URL}/movie/{radarr_id}"
    headers = {"X-Api-Key": API_KEY}
    params = {"deleteFiles": "true"}

    if DRY_RUN:
        print(f"RADARR :: DRY RUN :: Would have deleted {title} and freed up {convert_bytes(size_on_disk)}")
        return

    response = requests.delete(url, headers=headers, params=params)
    if response.status_code == 200:
        print(f"RADARR :: {title} deleted successfully. {convert_bytes(size_on_disk)} freed up")
    else:
        raise Exception(f"Deletion failed with status code {response.status_code}")
