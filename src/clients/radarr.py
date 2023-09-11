"""Radarr API client."""
import requests

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
        
    def __get_exempt_tag_ids(self, tag_names):
        url = f"{self.base_url}/tag"
        headers = {"X-Api-Key": self.api_key}

        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")
        
        tags = response.json()
        tag_ids = [tag["id"] for tag in tags if tag["label"] in tag_names]

        return tag_ids
            

    def __delete_media(self, movie_file_ids: set):
        url = f"{self.base_url}/moviefile/bulk"
        headers = {"X-Api-Key": self.api_key}
        body = {"movieFileIds": movie_file_ids}

        response = requests.delete(url, headers=headers, json=body, timeout=30)
        if response.status_code != 204:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")
        
        return True
    
    def get_and_delete_media(self, media_ids: set):
        """
        Gets and deletes media with the given ID from the Radarr API.
        
        Args:
            media_ids: The IDs of the media to delete.
            
        Returns:
            True if the media was deleted successfully.
            
        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        media = self.__get_media()
        exempt_tag_ids = self.__get_exempt_tag_ids(self.exempt_tag_names)

        movie_file_ids = list(set([
            movie.get("movieFile", {}).get("id")
            for movie in media
            if movie.get("tmdbId") in media_ids
            and not any(tag in exempt_tag_ids for tag in movie.get("tags", []))
            and movie.get("movieFile", {}).get("id") is not None
        ]))
            
        return self.__delete_media(movie_file_ids)