"""Module for interacting with Plex."""
import time
from datetime import datetime, timedelta
from collections import defaultdict
from plexapi.server import PlexServer
from src.logger import logger


class PlexClient:
    """Client for interacting with Plex."""

    def __init__(self, config):
        self.config = config
        self.base_url = config.plex.base_url
        self.token = config.plex.token
        self.plex = PlexServer(self.base_url, self.token)

    def __get_media(self, section_type):
        sections = self.__get_sections_by_type(section_type)

        media_list = []
        for section in sections:
            for media in section.all():
                media_list.append(media)

        return media_list

    def __get_sections_by_type(self, section_type):
        return [section for section in self.plex.library.sections() if section.type == section_type]
    
    def __get_episode_sessions(self):
        return [session for session in self.plex.sessions() if session.type == "episode"]
    
    def __get_series_by_guid(self, series_guid):
        sections = self.__get_sections_by_type("show")
        for section in sections:
            series = section.getGuid(series_guid)
            if series:
                return series
        
        return None
    
    def __get_episodes_prior_to_session(self, session):
        series = self.__get_series_by_guid(session.grandparentGuid)
        if not series:
            return False
        
        all_episodes = series.episodes()
        episodes_to_check = defaultdict(list)

        for episode in all_episodes:
            if episode.parentIndex < session.parentIndex or (episode.parentIndex == session.parentIndex and episode.index < session.index):
                logger.debug("[PLEX] S%sE%s is before S%sE%s. It should be checked to be unloaded.", episode.parentIndex, episode.index, session.parentIndex, session.index)
                series_tvdb_id = next((guid.id.split("tvdb://")[1].split("?")[0] for guid in series.guids if guid.id.startswith("tvdb://")), None)
                episodes_to_check[series_tvdb_id].append(episode)
            else:
                logger.debug("[PLEX] S%sE%s is after S%sE%s. It should not be unloaded.", episode.parentIndex, episode.index, session.parentIndex, session.index)

        return episodes_to_check
    
    def __media_is_expired(self, media, watched_media_expiry_seconds, unwatched_media_expiry_seconds):
        current_time = time.time()
        watched_media_expiry_date = datetime.fromtimestamp(current_time - watched_media_expiry_seconds)
        unwatched_media_expiry_date = datetime.fromtimestamp(current_time - unwatched_media_expiry_seconds)
        min_date = datetime.now() - timedelta(seconds=max(watched_media_expiry_seconds, unwatched_media_expiry_seconds))

        added_at = media.addedAt if media.addedAt else datetime.fromtimestamp(0)
        if media.type == "show":
            added_at = max(episode.addedAt for episode in media.episodes()) if media.episodes() else added_at
        history = media.history(mindate=min_date)
        watched_date = max(entry.viewedAt for entry in history) if history else None

        if added_at < unwatched_media_expiry_date and (watched_date is None or watched_date < watched_media_expiry_date):
            return True
        
        return False

    def __media_is_unloadable(self, media, session, watched_media_expiry_seconds=7776000):
        min_date = datetime.now() - timedelta(seconds=watched_media_expiry_seconds)
        history = media.history(mindate=min_date)
        for entry in history:
            if entry.accountID != session.user.id:
                logger.info("[PLEX] %s - S%sE%s has been watched by a different user. It should not be unloaded.", media.title, media.parentIndex, media.index)
                return False
            
        return True

    def get_expired_media(self, section_type, watched_media_expiry_seconds, unwatched_media_expiry_seconds):
        """
        Retrieves a list of expired media.
        
        Args:
            section_type: The type of media to retrieve.
            watched_media_expiry_seconds: The number of seconds after which watched media is considered expired.
            unwatched_media_expiry_seconds: The number of seconds after which unwatched media is considered expired.
            
        Returns:
            List[PlexMedia]: A list of PlexMedia objects representing the expired media.
        """
        media = self.__get_media(section_type)
        expired_media = []

        for item in media:
            if self.__media_is_expired(item, watched_media_expiry_seconds, unwatched_media_expiry_seconds):
                item.reload()
                expired_media.append(item)

        return expired_media
    
    def get_media_to_unload(self, watched_media_expiry_seconds):
        """
        Retrieves a list of media that should be unloaded.

        Args:
            watched_media_expiry_seconds: The number of seconds after which watched media is considered expired.

        Returns:
            List[PlexMedia]: A list of PlexMedia objects representing the media to unload.
        """
        sessions = self.__get_episode_sessions()
        media_to_unload = defaultdict(list)

        for session in sessions:
            episodes_dict = self.__get_episodes_prior_to_session(session)
            for key, episodes in episodes_dict.items():
                for episode in episodes:
                    if self.__media_is_unloadable(episode, session, watched_media_expiry_seconds):
                        episode.reload()
                        media_to_unload[key].append(episode)

        return media_to_unload
