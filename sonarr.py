import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("SONARR_API_KEY")
BASE_URL = os.getenv("SONARR_BASE_URL")

def get_sonarr_id(tvdb_id):
    """
    Retrieves the Sonarr ID and title of a TV series given its TVDB ID.

    Args:
        tvdb_id (int): The TVDB ID of the TV series.

    Returns:
        tuple: A tuple containing the Sonarr ID and title of the TV series.

    Raises:
        Exception: If the request to retrieve the Sonarr ID fails.
    """
    url = f"{BASE_URL}/series"
    headers = {"X-Api-Key": API_KEY}
    params = {"tvdbId": tvdb_id}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        series_data = response.json()
        if not series_data:
            return None, None
        return series_data[0]['id'], series_data[0]['title']
    else:
        raise Exception(f"Fetching Sonarr ID failed with status code {response.status_code}")
    
def find_and_delete_series(tvdb_id):
    """
    Finds a TV series in Sonarr by its TVDB ID and deletes it along with its files.

    Args:
        tvdb_id (int): The TVDB ID of the TV series.

    Raises:
        Exception: If the request to retrieve the Sonarr ID fails or if the deletion fails.
    """
    sonarr_id, title = get_sonarr_id(tvdb_id)
    if sonarr_id is None or title is None:
        raise Exception('Fetching Sonarr ID failed')
    
    delete_unplayed_series(sonarr_id, title)

def delete_unplayed_series(sonarr_id, title):
    """
    Deletes a TV series in Sonarr by its Sonarr ID along with its files.

    Args:
        sonarr_id (int): The Sonarr ID of the TV series.
        title (str): The title of the TV series.

    Raises:
        Exception: If the deletion fails.
    """
    url = f"{BASE_URL}/series/{sonarr_id}"
    headers = {"X-Api-Key": API_KEY}
    params = {'deleteFiles': 'true'}

    response = requests.delete(url, headers=headers, params=params)
    if response.status_code == 200:
        print(f"{title} deleted successfully.")
    else:
        raise Exception(f"Deletion failed with status code {response.status_code}")