import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("RADARR_API_KEY")
BASE_URL = os.getenv("RADARR_BASE_URL")

def get_radarr_id(tmdb_id):
    """
    Retrieves the Radarr ID and title of a movie given its TMDB ID.

    Args:
        tmdb_id (int): The TMDB ID of the movie.

    Returns:
        Tuple[int, str]: A tuple containing the Radarr ID and title of the movie.

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
            return None, None
        return movie_data[0]['id'], movie_data[0]['title']
    else:
        raise Exception(f"Fetching Radarr ID failed with status code {response.status_code}")
    
def find_and_delete_movie(tmdb_id):
    """
    Finds a movie in Radarr by its TMDB ID and deletes it if it has not been played.

    Args:
        tmdb_id (int): The TMDB ID of the movie.

    Raises:
        Exception: If the request to retrieve the Radarr ID fails or if the deletion fails.
    """
    radarr_id, title = get_radarr_id(tmdb_id)
    if radarr_id is None or title is None:
        raise Exception(f"Fetching Radarr ID failed")
    
    delete_unplayed_movie(radarr_id, title)

def delete_unplayed_movie(radarr_id, title):
    """
    Deletes a movie from Radarr given its ID and title, if it has not been played.

    Args:
        radarr_id (int): The ID of the movie in Radarr.
        title (str): The title of the movie.

    Raises:
        Exception: If the deletion fails.
    """
    url = f"{BASE_URL}/movie/{radarr_id}"
    headers = {"X-Api-Key": API_KEY}
    params = {'deleteFiles': 'true'}

    response = requests.delete(url, headers=headers, params=params)
    if response.status_code == 200:
        print(f"{title} deleted successfully.")
    else:
        raise Exception(f"Deletion failed with status code {response.status_code}")