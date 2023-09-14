"""Module for interacting with the Overseerr API."""
import requests
from retry import retry
from src.logger import logger

class OverseerrClient:
    """
    Class for interacting with the Overseerr API.
    """
    def __init__(self, config):
        self.config = config
        self.api_key = config.overseerr.api_key
        self.base_url = config.overseerr.base_url
        self.fetch_limit = config.overseerr.fetch_limit

    def __get_media(self):
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
        url = f"{self.base_url}/media/{media_id}"
        headers = {"X-API-KEY": self.api_key}

        response = requests.delete(url, headers=headers, timeout=30)
        if response.status_code != 204:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

    @retry(tries=3, delay=5)
    def get_and_delete_media(self, media_to_delete: dict, dry_run: bool = False):
        """
        Gets and deletes media with the given IDs from the Overseerr API.

        Args:
            media_to_delete: A dictionary where the key is the ID of the media to delete 
            and the value is the title of the media.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        media = self.__get_media()

        if media is None:
            return

        media_type_id_map = {"movie": "tmdbId", "tv": "tvdbId"}

        for media_id, media_title in media_to_delete.items():
            for item in media:
                media_type = item.get("mediaType")
                if media_type is None:
                    continue

                media_id_key = media_type_id_map.get(media_type)
                if media_id_key and item.get(media_id_key) == int(media_id):
                    if dry_run:
                        logger.info("[OVERSEERR][DRY RUN] Would have deleted %s.", media_title)
                        continue

                    try:
                        self.__delete_media(item.get("id"))
                        logger.info("[OVERSEERR] Deleted %s.", media_title)
                    except requests.exceptions.RequestException as err:
                        logger.error("[OVERSEERR] Failed to delete %s. Error: %s", media_title, err)
                        continue
