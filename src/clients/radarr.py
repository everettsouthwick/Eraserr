"""Radarr API client."""
import requests
from src.logger import logger
from src.util import convert_bytes

class RadarrClient:
    """Class for interacting with the Radarr API."""
    def __init__(self, config):
        self.config = config
        self.api_key = config.radarr.api_key
        self.base_url = config.radarr.base_url
        self.exempt_tag_names = config.radarr.exempt_tag_names

    def __get_media(self):
        url = f"{self.base_url}/movie"
        headers = {"X-Api-Key": self.api_key}

        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

        return response.json()

    def __get_exempt_tag_ids(self, tag_names: list):
        url = f"{self.base_url}/tag"
        headers = {"X-Api-Key": self.api_key}

        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

        tags = response.json()
        tag_ids = [tag["id"] for tag in tags if tag["label"] in tag_names]

        return tag_ids

    def __delete_media(self, media_id: int):
        url = f"{self.base_url}/movie/{media_id}"
        headers = {"X-Api-Key": self.api_key}
        params = {"deleteFiles": True, "addImportExclusion": False}

        response = requests.delete(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

    def get_and_delete_media(self, media_to_delete: dict, dry_run: bool = False):
        """
        Gets and deletes media with the given ID from the Radarr API.
        
        Args:
            media_to_delete: A dictionary where the key is the ID of the media to delete and the value is the title of the media.
            dry_run: Whether to perform a dry run.
            
        Returns:
            None.
            
        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        media = self.__get_media()
        exempt_tag_ids = self.__get_exempt_tag_ids(self.exempt_tag_names)

        total_size = 0

        for movie in media:
            if str(movie.get("tmdbId")) not in media_to_delete.keys():
                continue

            if any(tag in exempt_tag_ids for tag in movie.get("tags", [])):
                media_to_delete.pop(str(movie.get("tmdbId")))
                logger.info("[RADARR] Skipping %s because it is exempt.", movie.get("title"))
                continue

            if movie.get("id") is not None:
                total_size += movie.get("sizeOnDisk", 0)
                if dry_run:
                    logger.info("[RADARR][DRY RUN] Would have deleted %s. Freed: %s.", movie.get("title"), convert_bytes(movie.get("sizeOnDisk", 0)))
                    continue

                try:
                    self.__delete_media(movie.get("id"))
                    logger.info("[RADARR] Deleted %s. Freed: %s.", movie.get("title"), convert_bytes(movie.get("sizeOnDisk", 0)))
                except requests.exceptions.RequestException as err:
                    logger.error("[RADARR] Failed to delete %s. Error: %s", movie.get("title"), err)
                    continue

        if dry_run and total_size > 0:
            logger.info("[RADARR][DRY RUN] Would have total freed: %s.", convert_bytes(total_size))
        elif total_size > 0:
            logger.info("[RADARR] Total freed: %s.", convert_bytes(total_size))

        return media_to_delete
