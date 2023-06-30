import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OVERSEERR_API_KEY")
BASE_URL = os.getenv("OVERSEERR_BASE_URL")

DEFAULT_FETCH_LIMIT = 10
FETCH_LIMIT = int(os.getenv("OVERSEERR_FETCH_LIMIT"), DEFAULT_FETCH_LIMIT)

def fetch_overseerr_requests():
    """
    Fetches a list of requests from the Overseerr API.

    Returns:
        A list of request objects.
    Raises:
        Exception: If the API request fails.
    """
    url = f"{BASE_URL}/request"
    headers = {"X-API-KEY": API_KEY}

    requests_list = []
    page = 1
    max_executions_allowed = 1000

    while True and max_executions_allowed > 0:
        params = {
            "take": FETCH_LIMIT, 
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Fetching Overseerr requests failed with status code {response.status_code}")
        
        request_data = response.json()

        # Break loop if no more data
        if not request_data['results']:
            break
        
        requests_list.extend(request_data['results'])

        # Increment the 'page' parameter for the next iteration
        page += 1
        max_executions_allowed -= 1

    return requests_list


def find_and_delete_request(item_id):
    """
    Finds and deletes a request with the given item ID from the Overseerr API.

    Args:
        item_id: The ID of the item to delete.

    Returns:
        None
    """
    requests = fetch_overseerr_requests()
    if requests is None:
        return

    for request in requests:
        if 'media' in request and 'mediaType' in request['media'] and 'tv' in request['media']['mediaType'] and 'tvdbId' in request['media'] and request['media']['tvdbId'] == item_id:
            delete_request(request['id'])
        elif 'media' in request and 'mediaType' in request['media'] and 'movie' in request['media']['mediaType'] and 'tmdbId' in request['media'] and request['media']['tmdbId'] == item_id:
            delete_request(request['id'])

def delete_request(request_id):
    """
    Deletes a request with the given ID from the Overseerr API.

    Args:
        request_id (int): The ID of the request to delete.

    Returns:
        None

    Raises:
        Exception: If the API request fails.
    """
    url = f"{BASE_URL}/request/{request_id}"
    headers = {"X-API-KEY": API_KEY}

    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print(f"Request {request_id} deleted successfully.")
    else:
        raise Exception(f"Deletion of request {request_id} failed with status code {response.status_code}")
