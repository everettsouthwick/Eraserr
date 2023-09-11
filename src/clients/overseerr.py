import requests

class OverseerrClient:
    def __init__(self, config):
        self.config = config
        self.api_key = config.overseerr.api_key
        self.base_url = config.overseerr.base_url
        self.fetch_limit = config.overseerr.fetch_limit
        self.dry_run = config.dry_run

    def fetch_overseerr_media(self):
        """
        Fetches a list of media from the Overseerr API.

        Returns:
            A list of media objects.
        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        url = f"{self.base_url}/media"
        headers = {"X-API-KEY": self.api_key}

        media_list = []
        skip = 0
        max_executions_allowed = 1000

        while max_executions_allowed > 0:
            params = {
                "take": self.fetch_limit,
                "skip": skip,
            }

            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code != 200:
                raise requests.exceptions.RequestException(
                    f"Fetching Overseerr media failed with status code {response.status_code}"
                )

            request_data = response.json()

            # Break loop if no more data
            if not request_data["results"]:
                break

            media_list.extend(request_data["results"])

            # Increment the 'page' parameter for the next iteration
            skip += self.fetch_limit
            max_executions_allowed -= 1

        return media_list

    def find_and_delete_media(self, item_id):
        """
        Finds and deletes media with the given item ID from the Overseerr API.

        Args:
            item_id: The ID of the item to delete.

        Returns:
            None
        """
        media = self.fetch_overseerr_media()
        if media is None:
            return

        for item in media:
            if item["mediaType"] is None:
                continue

            if item["mediaType"] == "movie" and item["tmdbId"] == int(item_id):
                self.delete_media(item["id"])
                break

            if item["mediaType"] == "tv" and item["tvdbId"] == int(item_id):
                self.delete_media(item["id"])
                break

    def delete_media(self, media_id):
        """
        Deletes media with the given ID from the Overseerr API.

        Args:
            media_id (int): The ID of the media to delete.

        Returns:
            None

        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        url = f"{self.base_url}/media/{media_id}"
        headers = {"X-API-KEY": self.api_key}

        if self.dry_run:
            print(f"OVERSEERR :: DRY RUN :: Would have deleted media {media_id}")
            return

        response = requests.delete(url, headers=headers, timeout=30)
        if response.status_code == 204:
            print(f"OVERSEERR :: Media {media_id} deleted successfully.")
        else:
            raise requests.exceptions.RequestException(
                f"Deletion of media {media_id} failed with status code {response.status_code}"
            )
