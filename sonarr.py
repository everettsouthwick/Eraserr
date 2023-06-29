import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("SONARR_API_KEY")
BASE_URL = os.getenv("SONARR_BASE_URL")

def get_sonarr_id(tvdb_id):
    url = f"{BASE_URL}/series"
    headers = {"X-Api-Key": API_KEY}
    params = {"tvdbId": tvdb_id}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        series_data = response.json()
        if not series_data:
            return None
        return series_data[0]['id']
    else:
        print(f"Fetching Sonarr ID failed with status code {response.status_code}")
        return None

def delete_unplayed_series(sonarr_id):
    url = f"{BASE_URL}/series/{sonarr_id}"
    headers = {"X-Api-Key": API_KEY}
    params = {'deleteFiles': 'true'}

    response = requests.delete(url, headers=headers, params=params)
    if response.status_code == 200:
        print("Series deleted successfully.")
    else:
        print(f"Deletion failed with status code {response.status_code}")
