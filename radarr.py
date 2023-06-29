import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("RADARR_API_KEY")
BASE_URL = os.getenv("RADARR_BASE_URL")

def get_radarr_id(tmdb_id):
    url = BASE_URL
    headers = {"X-Api-Key": API_KEY}
    params = {"tmdbId": tmdb_id}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        movie_data = response.json()
        if not movie_data:
            return None
        return movie_data[0]['id']
    else:
        print(f"Fetching Radarr ID failed with status code {response.status_code}")
        return None

def delete_unplayed_movie(radarr_id):
    url = f"{BASE_URL}/{radarr_id}"
    headers = {"X-Api-Key": API_KEY}
    params = {'deleteFiles': 'true'}

    response = requests.delete(url, headers=headers, params=params)
    if response.status_code == 200:
        print("Movie deleted successfully.")
    else:
        print(f"Deletion failed with status code {response.status_code}")