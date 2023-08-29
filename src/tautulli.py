import requests
import time
from datetime import datetime


class TautulliClient:
    def __init__(self, config):
        self.config = config
        self.api_key = config.tautulli.api_key
        self.base_url = config.tautulli.base_url
        self.fetch_limit = config.tautulli.fetch_limit
        self.last_watched_days_deletion_threshold = config.last_watched_days_deletion_threshold
        self.unwatched_days_deletion_threshold = config.unwatched_days_deletion_threshold

    def fetch_libraries(self, section_type):
        params = {"apikey": self.api_key, "cmd": "get_libraries"}

        response = requests.get(self.base_url, params=params, timeout=30)

        if response.status_code != 200:
            raise requests.exceptions.RequestException(
                f"Fetching libraries failed with status code {response.status_code}"
            )

        libraries = response.json()
        section_ids = []

        if not libraries["response"]["data"]:
            return section_ids

        section_ids = [
            library["section_id"]
            for library in libraries["response"]["data"]
            if library["section_type"] == section_type
        ]
        return section_ids

    def fetch_metadata(self, rating_key):
        """
        Fetches metadata for a given rating key.

        Args:
            rating_key (str): The rating key for the media item.

        Returns:
            str: The item ID for the media item, or None if it could not be found.
        """
        params = {"apikey": self.api_key, "cmd": "get_metadata", "rating_key": rating_key}

        response = requests.get(self.base_url, params=params, timeout=30)

        if response.status_code != 200:
            raise requests.exceptions.RequestException(
                f"Metadata request for rating_key {rating_key} failed with status code {response.status_code}"
            )

        metadata = response.json()

        if not metadata["response"]["data"]:
            return None

        item_id = None
        for guid in metadata["response"]["data"]["guids"]:
            if "movie" in metadata["response"]["data"]["media_type"]:
                if "tmdb://" in guid:
                    item_id = guid.replace("tmdb://", "")
                    break
            elif "show" in metadata["response"]["data"]["media_type"]:
                if "tvdb://" in guid:
                    item_id = guid.replace("tvdb://", "")
                    break

        return item_id

    def refresh_library_in_section(self, section_id):
        """
        Refreshes the specified section's library by fetching the latest media information.

        Args:
            section_id (int): The ID of the section to refresh.

        Returns:
            None

        """
        params = {
            "apikey": self.api_key,
            "cmd": "get_library_media_info",
            "section_id": section_id,
            "length": self.fetch_limit,
            "refresh": "true",
        }

        requests.get(self.base_url, params=params, timeout=30)

    def refresh_library(self, section_ids, section_type):
        """
        Refreshes the specified section's library by fetching the latest media information.

        Args:
            section_ids (list): The IDs of the sections to refresh.

        Returns:
            None

        """
        for section_id in section_ids:
            self.refresh_library_in_section(section_id)

        print(f"TAUTULLI :: Library refresh complete for {section_type}")

    def fetch_and_count_unplayed_titles_in_section(self, section_id):
        """
        Fetches the unplayed titles for a given section ID and counts them.

        Args:
            section_id (int): The section ID to fetch unplayed titles for.

        Returns:
            tuple: A tuple containing the count of unplayed titles and a list of their item IDs.
        """
        count = 0
        item_ids = []
        last_watched_threshold_timestamp = time.time() - self.last_watched_days_deletion_threshold * 24 * 60 * 60
        unwatched_threshold_timestamp = time.time() - self.unwatched_days_deletion_threshold * 24 * 60 * 60
        start = 0
        max_executions_allowed = 1000
        is_first_loop = True

        while max_executions_allowed > 0:
            params = {
                "apikey": self.api_key,
                "cmd": "get_library_media_info",
                "section_id": section_id,
                "order_column": "last_played",
                "order_dir": "asc",
                "length": self.fetch_limit,
                "start": start,
                "refresh": "true" if is_first_loop else "false",
            }

            response = requests.get(self.base_url, params=params, timeout=30)

            if response.status_code != 200:
                raise requests.exceptions.RequestException(
                    f"Library media info request for section_id {section_id} failed with status code {response.status_code}"
                )

            data = response.json()

            # Break loop if no more data
            if not data["response"]["data"]["data"]:
                break

            for item in data["response"]["data"]["data"]:
                rating_key = item["rating_key"]

                item_id = self.fetch_metadata(rating_key)

                if item_id is not None:
                    if item["added_at"] != "":
                        if (item["last_played"] is None or item["last_played"] == "") and int(item["added_at"]) < unwatched_threshold_timestamp:
                            count += 1
                            item_ids.append(item_id)
                        elif (
                            (item["last_played"] is not None or item["last_played"] == "") and int(item["last_played"]) < last_watched_threshold_timestamp
                        ):
                            count += 1
                            item_ids.append(item_id)
                    else:
                        print(f"TAUTULLI :: {item['title']} is missing the added_at tag, skipping...")

            # Increment the 'start' parameter for the next iteration
            start += self.fetch_limit
            max_executions_allowed -= 1
            is_first_loop = False

        return count, item_ids

    def fetch_and_count_unplayed_titles(self, section_ids):
        """
        Fetches and counts the number of unplayed titles in the specified sections.

        Args:
            section_ids (list): A list of section IDs to search for unplayed titles.

        Returns:
            tuple: A tuple containing the total count of unplayed titles and a list of all item IDs.

        """
        total_count = 0
        all_item_ids = []

        for section_id in section_ids:
            count, item_ids = self.fetch_and_count_unplayed_titles_in_section(section_id)
            total_count += count
            all_item_ids.extend(item_ids)

        print(f"TAUTULLI :: There are {total_count} items eligible for deletion. IDs: {all_item_ids}")

        return all_item_ids
