"""Sonarr API client."""
from datetime import datetime
import requests
from retry import retry
from src.logger import logger
from src.util import convert_bytes

class SonarrClient:
    """Class for interacting with the Sonarr API."""
    def __init__(self, config):
        self.config = config
        self.api_key = config.sonarr.api_key
        self.base_url = config.sonarr.base_url
        self.monitor_continuing_series = config.sonarr.monitor_continuing_series
        self.exempt_tag_names = config.sonarr.exempt_tag_names
        self.dynamic_load = config.sonarr.dynamic_load

    def __get_media(self):
        url = f"{self.base_url}/series"
        headers = {"X-Api-Key": self.api_key}

        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

        return response.json()
    
    def __get_media_by_id(self, media_id: int):
        url = f"{self.base_url}/series/{media_id}"
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

    def __get_media_episodes(self, media_id: int):
        url = f"{self.base_url}/episode"
        headers = {"X-Api-Key": self.api_key}
        params = {"seriesId": media_id}

        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

        return response.json()

    def __search_media_episodes(self, episode_ids: list):
        url = f"{self.base_url}/command"
        headers = {"X-Api-Key": self.api_key}
        body = {"name": "EpisodeSearch", "episodeIds": episode_ids}

        response = requests.post(url, headers=headers, json=body, timeout=30)
        if response.status_code != 201:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

        return response.json()

    def __put_media(self, series):
        url = f"{self.base_url}/series/{series.get('id')}"
        headers = {"X-Api-Key": self.api_key}

        response = requests.put(url, headers=headers, json=series, timeout=30)
        if response.status_code != 202:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

        return response.json()

    def __monitor_media_episodes(self, episode_ids: list, monitored: bool = False):
        url = f"{self.base_url}/episode/monitor"
        headers = {"X-Api-Key": self.api_key}
        body = {"episodeIds": episode_ids, "monitored": monitored}

        response = requests.put(url, headers=headers, json=body, timeout=30)
        if response.status_code != 202:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

    def __unmonitor_empty_seasons(self, series):
        for season in series.get("seasons", []):
            if season.get("statistics", {}).get("episodeCount", 0) > 0:
                continue

            if season.get("monitored", False):
                season["monitored"] = False

        return series

    def __delete_media(self, media_id: int):
        url = f"{self.base_url}/series/{media_id}"
        headers = {"X-Api-Key": self.api_key}
        params = {"deleteFiles": True, "addImportListExclusion": False}

        response = requests.delete(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")
  
    def __delete_media_episodes(self, episode_file_ids: list):
        url = f"{self.base_url}/episodefile/bulk"
        headers = {"X-Api-Key": self.api_key}
        body = {"episodeFileIds": episode_file_ids}

        response = requests.delete(url, headers=headers, json=body, timeout=60)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"{response.url} : {response.status_code} - {response.text}")

    def __handle_ended_series(self, series, dry_run: bool = False):
        size_on_disk = series.get("statistics", {}).get("sizeOnDisk", 0)
        if dry_run:
            logger.info("[SONARR][DRY RUN] Would have deleted %s. Space freed: %s.", series.get("title"), convert_bytes(size_on_disk))
            return size_on_disk
        
        try:
            self.__delete_media(series.get("id"))
            logger.info("[SONARR] Deleted %s. Space freed: %s.", series.get("title"), convert_bytes(size_on_disk))
        except requests.exceptions.RequestException as err:
            logger.error("[SONARR] Failed to delete %s. Error: %s", series.get("title"), err)

        return series.get("statistics", {}).get("sizeOnDisk", 0)

    def __handle_continuing_series(self, series, dry_run: bool = False):
        episodes = self.__get_media_episodes(series.get("id"))
        filtered_episodes = [episode for episode in episodes if episode['seasonNumber'] != 0]
        sorted_episodes = sorted(filtered_episodes, key=lambda x: (x['seasonNumber'], x['episodeNumber']))
        episodes_to_unload = sorted_episodes[self.dynamic_load.episodes_to_load:]

        unmonitor_episode_ids = []
        delete_episode_file_ids = []

        for episode in episodes_to_unload:
            if episode.get("monitored", False):
                unmonitor_episode_ids.append(episode.get("id"))
            if episode.get("hasFile", False) and episode.get("episodeFileId") not in delete_episode_file_ids:
                delete_episode_file_ids.append(episode.get("episodeFileId"))

        size_on_disk = 0

        if dry_run:
            logger.info("[SONARR][DRY RUN] Would have unmonitored %s.", series.get("title"))
            return size_on_disk

        try:
            if unmonitor_episode_ids:
                self.__monitor_media_episodes(unmonitor_episode_ids, False)
                logger.info("[SONARR] Unmonitored %s.", series.get("title"))
            if delete_episode_file_ids:
                self.__delete_media_episodes(delete_episode_file_ids)
                original_size_on_disk = series.get("statistics", {}).get("sizeOnDisk", 0)
                series = self.__get_media_by_id(series.get("id"))
                series = self.__unmonitor_empty_seasons(series)
                series = self.__put_media(series)
                size_on_disk = original_size_on_disk - series.get("statistics", {}).get("sizeOnDisk", 0)
  
        except requests.exceptions.RequestException as err:
            logger.error("[SONARR] Failed to unmonitor %s. Error: %s", series.get("title"), err)
            return size_on_disk

        return size_on_disk

    def __get_episodes_to_load_and_unload(self, series, dynamic_media):
        episodes = self.__get_media_episodes(series.get("id"))
        filtered_episodes = [episode for episode in episodes if episode.get("seasonNumber", -1) != 0 and episode.get("airDate") < datetime.now().isoformat()]
        sorted_episodes = sorted(filtered_episodes, key=lambda x: (x['seasonNumber'], x['episodeNumber']))
        episode_index = next((index for (index, episode) in enumerate(sorted_episodes) if episode.get("seasonNumber", 0) == dynamic_media.season and episode.get("episodeNumber", 0) == dynamic_media.episode), None)
        if episode_index is not None:
            load_index_start = episode_index + 1
            load_index_end = episode_index + self.dynamic_load.episodes_to_keep + 1

            episodes_to_load = sorted_episodes[load_index_start:load_index_end] if load_index_end >= load_index_start else []

            unload_index_start = self.dynamic_load.episodes_to_keep
            unload_index_end = episode_index - self.dynamic_load.episodes_to_keep

            episodes_to_unload = sorted_episodes[unload_index_start:unload_index_end] if unload_index_end >= unload_index_start else []
        return episodes_to_load, episodes_to_unload

    def __handle_episode_loading(self, episodes_to_load, series, dry_run):
        monitor_episode_ids = []
        search_episode_ids = []
        for episode in episodes_to_load:
            if not episode.get("monitored", False):
                monitor_episode_ids.append(episode["id"])
            if not episode.get("hasFile", False):
                self.__log_episode_loading(episode, series, dry_run)
                search_episode_ids.append(episode["id"])
        if not dry_run:
            if monitor_episode_ids:
                self.__monitor_media_episodes(monitor_episode_ids, True)
            if search_episode_ids:
                self.__search_media_episodes(search_episode_ids)

    def __log_episode_loading(self, episode, series, dry_run):
        if dry_run:
            logger.info("[SONARR][DYNAMIC LOAD][DRY RUN] Would have loaded S%sE%s of %s", episode.get("seasonNumber"), episode.get("episodeNumber"), series.get("title"))
        else:
            logger.info("[SONARR][DYNAMIC LOAD] Loading S%sE%s of %s", episode.get("seasonNumber"), episode.get("episodeNumber"), series.get("title"))

    def __handle_episode_unloading(self, episodes_to_unload, series, dry_run):
        unmonitor_episode_ids = []
        delete_episode_file_ids = []
        for episode in episodes_to_unload:
            if episode.get("monitored", True):
                unmonitor_episode_ids.append(episode.get("id"))
            if episode.get("hasFile", True):
                self.__log_episode_unloading(episode, series, dry_run)
                if episode.get("episodeFileId") not in delete_episode_file_ids:
                    delete_episode_file_ids.append(episode.get("episodeFileId"))
        size_on_disk = 0
        if not dry_run:
            if unmonitor_episode_ids:
                self.__monitor_media_episodes(unmonitor_episode_ids, False)
            if delete_episode_file_ids:
                self.__delete_media_episodes(delete_episode_file_ids)
                original_size_on_disk = series.get("statistics", {}).get("sizeOnDisk", 0)
                series = self.__get_media_by_id(series.get("id"))
                series = self.__unmonitor_empty_seasons(series)
                series = self.__put_media(series)
                size_on_disk = original_size_on_disk - series.get("statistics", {}).get("sizeOnDisk", 0)
        return size_on_disk

    def __log_episode_unloading(self, episode, series, dry_run):
        if dry_run:
            logger.info("[SONARR][DYNAMIC LOAD][DRY RUN] Would have unloaded S%sE%s of %s", episode.get("seasonNumber"), episode.get("episodeNumber"), series.get("title"))
        else:
            logger.info("[SONARR][DYNAMIC LOAD] Unloading S%sE%s of %s", episode.get("seasonNumber"), episode.get("episodeNumber"), series.get("title"))

    def __handle_dynamic_load(self, series, dynamic_media, dry_run: bool = False):
        episodes_to_load, episodes_to_unload = self.__get_episodes_to_load_and_unload(series, dynamic_media)
        size_on_disk = 0
        self.__handle_episode_loading(episodes_to_load, series, dry_run)
        if not dynamic_media.unload:
            return size_on_disk
        size_on_disk = self.__handle_episode_unloading(episodes_to_unload, series, dry_run)
        return size_on_disk

    @retry(tries=3, delay=5)
    def get_and_delete_media(self, media_to_delete: dict, dry_run: bool = False):
        """
        Gets and deletes media with the given ID from the Sonarr API.
        
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
        original_deletion_count = len(media_to_delete)
        exempt_count = 0

        total_size = 0

        for series in media:
            if str(series.get("tvdbId")) not in media_to_delete.keys():
                continue

            if any(tag in exempt_tag_ids for tag in series.get("tags", [])):
                media_to_delete.pop(str(series.get("tvdbId")))
                exempt_count += 1
                logger.info("[SONARR] Skipping %s because it is exempt.", series.get("title"))
                continue

            if series.get("id") is not None:
                ended = series.get("ended", False)
                if not self.monitor_continuing_series or ended:
                    total_size += self.__handle_ended_series(series, dry_run)
                else:
                    total_size += self.__handle_continuing_series(series, dry_run)

        if dry_run:
            logger.info("[SONARR][DRY_RUN] Total series: %s. Series eligible for deletion: %s. Series deleted: %s. Series exempt: %s. Total space freed: %s.", len(media), original_deletion_count, len(media_to_delete), exempt_count, convert_bytes(total_size))
        else:
            logger.info("[SONARR] Total series: %s. Series eligible for deletion: %s. Series deleted: %s. Series exempt: %s. Total space freed: %s.", len(media), original_deletion_count, len(media_to_delete), exempt_count, convert_bytes(total_size))

        return media_to_delete

    @retry(tries=3, delay=5)
    def get_dynamic_load_media(self, media_to_load: dict, dry_run: bool = False):
        """
        Gets and deletes media with the given ID from the Sonarr API.
        
        Args:
            media_to_load: A dictionary where the key is the ID of the media to load and the value is the title of the media.
            dry_run: Whether to perform a dry run.
            
        Returns:
            None.
        
        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        media = self.__get_media()
        exempt_tag_ids = self.__get_exempt_tag_ids(self.exempt_tag_names)

        total_size = 0

        for series in media:
            if str(series.get("tvdbId")) not in media_to_load.keys():
                continue

            if any(tag in exempt_tag_ids for tag in series.get("tags", [])):
                media_to_load.pop(str(series.get("tvdbId")))
                logger.info("[SONARR][DYNAMIC LOAD] Skipping %s because it is exempt.", series.get("title"))
                continue

            if series.get("id") is not None:
                dynamic_media = media_to_load.get(str(series.get("tvdbId")))
                if dynamic_media is not None:
                    total_size += self.__handle_dynamic_load(series, dynamic_media, dry_run)

        if dry_run and total_size > 0:
            logger.info("[SONARR][DYNAMIC LOAD][DRY RUN] Would have total space freed: %s.", convert_bytes(total_size))
        elif total_size > 0:
            logger.info("[SONARR][DYNAMIC LOAD] Total space freed: %s.", convert_bytes(total_size))

        return media_to_load
