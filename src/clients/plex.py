"""Module for interacting with Plex."""
import time
from datetime import datetime, timedelta
from plexapi.server import PlexServer


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

    # def get_currently_playing(self):
    #     """
    #     Retrieves a list of currently playing TV series.

    #     Returns:
    #         List[PlexSeries]: A list of PlexSeries objects representing the currently playing TV series.
    #     """
    #     series = []
    #     sessions = self.plex._server.sessions()
    #     for session in sessions:
    #         if not session.type == "episode":
    #             continue

    #         series_guid = session.grandparentGuid
    #         sections = self.get_sections("show")
    #         for section in sections:
    #             show = section.getGuid(series_guid)
    #             if show:
    #                 parsed_series = self.parse_series(show, session.parentIndex, session.index)
    #                 series.append(parsed_series)
    #                 break
        
    #     return series
    
