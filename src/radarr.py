import requests
from src.util import convert_bytes
from src.models.radarr.radarrmovie import RadarrMovie


class RadarrClient:
    def __init__(self, config):
        self.config = config
        self.api_key = config.radarr.api_key
        self.base_url = config.radarr.base_url
        self.exempt_tag_names = config.radarr.exempt_tag_names
        self.dry_run = config.dry_run

    def get_movies(self):
        """
        Retrieves all movies from Radarr.

        Returns:
            RadarrMovie[]: A list of RadarrMovie objects.

        Raises:
            requests.exceptions.RequestException: If the request to retrieve the movies fails.
        """
        url = f"{self.base_url}/movie"
        headers = {"X-Api-Key": self.api_key}
        exempt_tag_ids = self.get_radarr_tag_ids(self.exempt_tag_names) if self.exempt_tag_names else []

        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            movies = []
            movie_data = response.json()
            for movie in movie_data:
                movie_obj = self.parse_movie(movie, exempt_tag_ids)
                movies.append(movie_obj)
            return movies

        raise requests.exceptions.RequestException(f"Fetching movies failed with status code {response.status_code}")

    def parse_movie(self, movie, exempt_tag_ids):
        """
        Parses a Radarr movie object into a RadarrMovie object.

        Args:
            movie (dict): The Radarr movie object to parse.

        Returns:
            RadarrMovie: A RadarrMovie object representing the movie.
        """
        tmdb_id = movie["tmdbId"] if "tmdbId" in movie else None
        imdb_id = movie["imdbId"] if "imdbId" in movie else None
        path = movie["path"] if "path" in movie else None
        title = movie["title"] if "title" in movie else None
        movie_file_id = movie["movieFile"]["id"] if "movieFile" in movie and "id" in movie["movieFile"] else None
        tags = movie["tags"] if "tags" in movie else []
        exempt = any(tag in exempt_tag_ids for tag in tags) if exempt_tag_ids else False

        return RadarrMovie(tmdb_id, imdb_id, path, title, movie_file_id, tags, exempt)

    def get_radarr_tag_ids(self, tag_names):
        """
        Retrieves the Radarr tag ID given its name.

        Args:
            tag_name (str): The name of the tag.

        Returns:
            int[]: The IDs of the exempted tag names.

        Raises:
            requests.exceptions.RequestException: If the request to retrieve the Radarr tag ID fails.
        """
        url = f"{self.base_url}/tag"
        headers = {"X-Api-Key": self.api_key}

        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            tag_ids = []
            tags = response.json()
            for tag in tags:
                if tag["label"] in tag_names:
                    tag_ids.append(tag["id"])
            return tag_ids
        else:
            raise requests.exceptions.RequestException(
                f"Fetching Radarr tag ID failed with status code {response.status_code}"
            )

    def get_radarr_id(self, tmdb_id):
        """
        Retrieves the Radarr ID, title, and size on disk of a movie given its TMDB ID.

        Args:
            tmdb_id (int): The TMDB ID of the movie.

        Returns:
            Tuple[int, str, int, int[]]: A tuple containing the Radarr ID, title, size on disk and tags of the movie.

        Raises:
            requests.exceptions.RequestException: If the request to retrieve the Radarr ID fails.
        """
        url = f"{self.base_url}/movie"
        headers = {"X-Api-Key": self.api_key}
        params = {"tmdbId": tmdb_id}

        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            movie_data = response.json()
            if not movie_data:
                return None, None, None, None
            return movie_data[0]["id"], movie_data[0]["title"], movie_data[0]["sizeOnDisk"], movie_data[0]["tags"]

        raise requests.exceptions.RequestException(f"Fetching Radarr ID failed with status code {response.status_code}")

    def find_and_delete_movie(self, tmdb_id):
        """
        Finds a movie in Radarr given its TMDB ID and deletes it if it has not been played.

        Args:
            tmdb_id (int): The TMDB ID of the movie.

        Returns:
            Tuple[boolean, int]: A tuple containing whether the movie was deleted and the size of the movie that was deleted in bytes.

        Raises:
            requests.exceptions.RequestException: If the request to retrieve the Radarr ID fails or if the deletion fails.
        """
        exempt_tag_ids = self.get_radarr_tag_ids(self.exempt_tag_names)
        radarr_id, title, size_on_disk, tags = self.get_radarr_id(tmdb_id)
        if radarr_id is None or title is None:
            raise requests.exceptions.RequestException("Fetching Radarr ID failed")

        if exempt_tag_ids is not None and tags is not None and any(tag in exempt_tag_ids for tag in tags):
            print(f"RADARR :: {title} is exempt from deletion")
            return False, 0

        deleted = self.delete_unplayed_movie(radarr_id, title, size_on_disk)

        return deleted, size_on_disk

    def delete_unplayed_movie(self, radarr_id, title, size_on_disk):
        """
        Deletes a movie in Radarr given its ID, title, and size on disk if it has not been played.

        Args:
            radarr_id (int): The ID of the movie in Radarr.
            title (str): The title of the movie.
            size_on_disk (int): The size of the movie on disk in bytes.

        Returns:
            boolean: Whether the movie was deleted.

        Raises:
            requests.exceptions.RequestException: If the deletion fails.
        """
        url = f"{self.base_url}/movie/{radarr_id}"
        headers = {"X-Api-Key": self.api_key}
        params = {"deleteFiles": "true"}

        if self.dry_run:
            print(f"RADARR :: DRY RUN :: Would have deleted {title} and freed up {convert_bytes(size_on_disk)}")
            return True

        response = requests.delete(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            print(f"RADARR :: {title} deleted successfully. {convert_bytes(size_on_disk)} freed up")
            return True

        raise requests.exceptions.RequestException(f"Deletion failed with status code {response.status_code}")
