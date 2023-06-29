import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OVERSEERR_API_KEY")
BASE_URL = os.getenv("OVERSEERR_BASE_URL")

FETCH_LIMIT = 1000 # How many requests to fetch

def fetch_overseerr_requests():
    url = f"{BASE_URL}/request"
    headers = {"X-API-KEY": API_KEY}
    params = {"take": FETCH_LIMIT}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        request_data = response.json()
        return request_data['results']
    else:
        print(f"Fetching Overseerr requests failed with status code {response.status_code}")
        return None

def find_and_delete_request(item_id):
    requests = fetch_overseerr_requests()
    if requests is None:
        return

    for request in requests:
        if 'media' in request and 'mediaType' in request['media'] and 'tv' in request['media']['mediaType'] and 'tvdbId' in request['media'] and request['media']['tvdbId'] == item_id:
            delete_request(request['id'])
        elif 'media' in request and 'mediaType' in request['media'] and 'movie' in request['media']['mediaType'] and 'tmdbId' in request['media'] and request['media']['tmdbId'] == item_id:
            delete_request(request['id'])

def delete_request(request_id):
    url = f"{BASE_URL}/request/{request_id}"
    headers = {"X-API-KEY": API_KEY}

    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print(f"Request {request_id} deleted successfully.")
    else:
        print(f"Deletion of request {request_id} failed with status code {response.status_code}")
