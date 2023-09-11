"""Module for interacting with the Overseerr API."""
import requests

class OverseerrClient:
    """
    Class for interacting with the Overseerr API.
    """
    def __init__(self, config):
        self.api_key = config.overseerr.api_key
        self.base_url = config.overseerr.base_url
        self.fetch_limit = config.overseerr.fetch_limit

    def __get_media(self):
        """
        Fetches all media from the Overseerr API.

        Returns:
            A list of media objects from the Overseerr API.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        url = f"{self.base_url}/media"
        headers = {"X-API-KEY": self.api_key}
        params = {"take": self.fetch_limit, "skip": 0}

        media_list = []

        for _ in range(1000):
            response = requests.get(url, headers=headers, params=params, timeout=30)
            if response.status_code != 200:
                raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")
            
            if not response.json().get("results", []):
                break
            
            media_list.extend(response.json().get("results", []))

            params["skip"] += self.fetch_limit

        return media_list

    def __delete_media(self, media_id: int):
        """
        Deletes media with the given ID from the Overseerr API.
        
        Args:
            media_id: The ID of the media to delete.
        
        Returns:
            True if the media was deleted successfully.
        
        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        url = f"{self.base_url}/media/{media_id}"
        headers = {"X-API-KEY": self.api_key}

        response = requests.delete(url, headers=headers, timeout=30)
        if response.status_code == 204:
            return True
        
        raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

    def get_and_delete_media(self, media_id: str):
        """
        Gets and deletes media with the given ID from the Overseerr API.

        Args:
            media_id: The ID of the media to delete.

        Returns:
            True if the media was deleted successfully.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        media = self.__get_media()

        if media is None:
            return False

        media_type_id_map = {"movie": "tmdbId", "tv": "tvdbId"}

        for item in media:
            media_type = item.get("mediaType")
            if media_type is None:
                continue

            media_id_key = media_type_id_map.get(media_type)
            if media_id_key and item.get(media_id_key) == int(media_id):
                return self.__delete_media(item["id"])

        return False
