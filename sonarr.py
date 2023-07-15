from util import convert_bytes
from dotenv import load_dotenv
import requests
import os

load_dotenv()

API_KEY = os.getenv("SONARR_API_KEY")
BASE_URL = os.getenv("SONARR_BASE_URL")
EXEMPT_TAG_NAME = os.getenv("SONARR_EXEMPT_TAG_NAME")

DRY_RUN = os.getenv("DRY_RUN", "False").lower() in ("true", "1", "t")


def get_sonarr_tag_id(tag_name):
    """
    Retrieves the Sonarr tag ID given its name.

    Args:
        tag_name (str): The name of the tag.

    Returns:
        int: The ID of the tag.

    Raises:
        requests.exceptions.RequestException: If the request to retrieve the Sonarr tag ID fails.
    """
    url = f"{BASE_URL}/tag"
    headers = {"X-Api-Key": API_KEY}

    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        tags = response.json()
        for tag in tags:
            if tag["label"] == tag_name:
                return tag["id"]
        return None
    raise requests.exceptions.RequestException(f"Fetching Sonarr tag ID failed with status code {response.status_code}")


def get_sonarr_item(tvdb_id):
    """
    Retrieves the Sonarr ID, title, and size on disk for a TV series with the given TVDB ID.

    Args:
        tvdb_id (int): The TVDB ID of the TV series.

    Returns:
        tuple: A tuple containing the Sonarr ID (int), title (str), and size on disk (int) of the TV series.

    Raises:
        requests.exceptions.RequestException: If the request to retrieve the Sonarr ID fails.
    """
    url = f"{BASE_URL}/series"
    headers = {"X-Api-Key": API_KEY}
    params = {"tvdbId": tvdb_id}

    response = requests.get(url, headers=headers, params=params, timeout=30)
    if response.status_code == 200:
        series = response.json()
        if not series:
            return None

        return series[0]

    raise requests.exceptions.RequestException(f"Fetching Sonarr ID failed with status code {response.status_code}")


def find_and_delete_series(tvdb_id):
    """
    Finds a TV series in Sonarr by its TVDB ID and deletes it along with its files.

    Args:
        tvdb_id (int): The TVDB ID of the TV series.

    Returns:
        Tuple[boolean, int]: A tuple containing whether the series was deleted or unmonitored and the size of the disk space freed up by deleting the TV series.

    Raises:
        requests.exceptions.RequestException: If the request to retrieve the Sonarr ID fails or if the deletion fails.
    """
    exempt_tag_id = get_sonarr_tag_id(EXEMPT_TAG_NAME)
    series = get_sonarr_item(tvdb_id)

    if series is None:
        raise requests.exceptions.RequestException("Fetching Sonarr ID failed")

    title = series["title"]
    size_on_disk = series["statistics"]["sizeOnDisk"]
    ended = series["ended"]
    tags = series["tags"]

    if exempt_tag_id is not None and tags is not None and exempt_tag_id in tags:
        print(f"SONARR :: {title} is exempt from deletion")
        return False, 0

    deleted = False
    if ended:
        deleted = delete_unplayed_series(series)
    else:
        deleted = unmonitor_unplayed_series(series)
        if deleted:
            series = get_sonarr_item(tvdb_id)
            has_unmonitored_episodes = True
            for season in series["seasons"]:
                if season["monitored"] is False and season["statistics"]["episodeFileCount"] > 0:
                    has_unmonitored_episodes = True
                    break

                has_unmonitored_episodes = False

            if has_unmonitored_episodes:
                size_on_disk = delete_unmonitored_episodes(series)

    return deleted, size_on_disk


def delete_unplayed_series(series):
    """
    Deletes a TV series in Sonarr by its Sonarr ID and deletes its files.

    Args:
        sonarr_id (int): The Sonarr ID of the TV series.
        title (str): The title of the TV series.
        size_on_disk (int): The size on disk of the TV series.

    Returns:
        boolean: Whether the series was deleted.

    Raises:
        Exception: If the deletion fails.
    """
    sonarr_id = series["id"]
    title = series["title"]
    size_on_disk = series["statistics"]["sizeOnDisk"]

    url = f"{BASE_URL}/series/{sonarr_id}"
    headers = {"X-Api-Key": API_KEY}
    params = {"deleteFiles": "true"}

    if DRY_RUN:
        print(f"SONARR :: DRY RUN :: {title} would be deleted. {convert_bytes(size_on_disk)} would be freed up")
        return True

    response = requests.delete(url, headers=headers, params=params, timeout=30)
    if response.status_code == 200:
        print(f"SONARR :: {title} deleted successfully. {convert_bytes(size_on_disk)} freed up")
        return True
    else:
        raise requests.exceptions.RequestException(f"Deletion failed with status code {response.status_code}")


def delete_unmonitored_episodes(series):
    """
    Deletes unmonitored episodes of a TV series in Sonarr by its Sonarr ID.

    Args:
        series (dict): A dictionary containing information about the TV series.

    Returns:
        int: The total size on disk of the deleted episodes.

    Raises:
        requests.exceptions.RequestException: If the deletion fails.
    """
    unmonitored_seasons = []
    for season in series["seasons"]:
        if not season["monitored"]:
            unmonitored_seasons.append(season["seasonNumber"])

    title = series["title"]
    episodes_deleted_count = 0
    size_on_disk = 0

    url = f"{BASE_URL}/episodefile"
    headers = {"X-Api-Key": API_KEY}
    params = {"seriesId": series["id"]}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        episodes = response.json()
        if not episodes:
            raise requests.exceptions.RequestException("Fetching Sonarr episodes failed")

        for episode in episodes:
            if episode["seasonNumber"] not in unmonitored_seasons:
                continue

            if DRY_RUN:
                size_on_disk += episode["size"]
                episodes_deleted_count += 1
                print(
                    f"SONARR :: DRY RUN :: {title} S{episode['seasonNumber']:02}E{episode['episodeNumber']:02} would be deleted. {convert_bytes(episode['size'])} would be freed up"
                )
                continue

            url = f"{BASE_URL}/episodefile/{episode['id']}"

            response = requests.delete(url, headers=headers, timeout=30)
            if response.status_code == 200:
                size_on_disk += episode["size"]
                episodes_deleted_count += 1
            else:
                raise requests.exceptions.RequestException(f"Deletion failed with status code {response.status_code}")
    else:
        raise requests.exceptions.RequestException(f"Fetching episodes failed with status code {response.status_code}")

    if DRY_RUN:
        print(
            f"SONARR :: DRY RUN :: {title} would have had {episodes_deleted_count} unmonitored episodes deleted. {convert_bytes(size_on_disk)} would be freed up"
        )
    else:
        print(
            f"SONARR :: {title} had {episodes_deleted_count} unmonitored episodes deleted. {convert_bytes(size_on_disk)} freed up"
        )

    return size_on_disk


def unmonitor_unplayed_series(series):
    """
    Unmonitors a TV series in Sonarr by its Sonarr ID.

    Args:
        sonarr_id (int): The Sonarr ID of the TV series.
        title (str): The title of the TV series.
        size_on_disk (int): The size on disk of the TV series.

    Returns:
        boolean: Whether the series was unmonitored.

    Raises:
        requests.exceptions.RequestException: If the unmonitoring fails.
    """
    url = f"{BASE_URL}/seasonpass"
    headers = {"X-Api-Key": API_KEY}
    title = series["title"]

    body = {
        "series": [series],
        "monitoringOptions": {"ignoreEpisodesWithFiles": True, "ignoreEpisodesWithoutFiles": True, "monitor": "future"},
    }

    if DRY_RUN:
        print(f"SONARR :: DRY RUN :: {title} would be unmonitored")
        return True

    response = requests.post(url, headers=headers, json=body, timeout=30)
    if response.status_code == 202:
        print(f"SONARR :: {title} unmonitored successfully")
        return True

    raise requests.exceptions.RequestException(f"Unmonitoring failed with status code {response.status_code}")
