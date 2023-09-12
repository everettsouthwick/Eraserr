"""
This module contains the JobRunner class, 
which is responsible for running the job function on a schedule.
"""
import time
import schedule
from src.clients.plex import PlexClient
from src.clients.radarr import RadarrClient
from src.clients.sonarr import SonarrClient
from src.clients.overseerr import OverseerrClient
from src.logger import logger

class JobRunner:
    """
    Class for running the job function on a schedule.
    """
    def __init__(self, config):
        self.config = config
        self.dry_run = config.dry_run
        self.schedule_interval = config.schedule_interval
        self.plex = PlexClient(config)
        self.radarr = RadarrClient(config)
        self.sonarr = SonarrClient(config)
        self.overseerr = OverseerrClient(config)
        self.dynamic_load = config.sonarr.dynamic_load
        self.radarr_enabled = config.radarr.enabled
        self.radarr_watched_deletion_threshold = config.radarr.watched_deletion_threshold
        self.radarr_unwatched_deletion_threshold = config.radarr.unwatched_deletion_threshold
        self.sonarr_enabled = config.sonarr.enabled
        self.sonarr_watched_deletion_threshold = config.sonarr.watched_deletion_threshold
        self.sonarr_unwatched_deletion_threshold = config.sonarr.unwatched_deletion_threshold
        self.overseerr_enabled = config.overseerr.enabled
        

    def run(self):
        """
        Runs the job function on a schedule.
        """
        self.get_and_delete_job()
        schedule.every(self.schedule_interval).seconds.do(self.get_and_delete_job)

        # if self.dynamic_load.enabled:
        #     self.dynamic_load_job()
        #     schedule.every(self.dynamic_load.schedule_interval).seconds.do(self.dynamic_load_job)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def get_and_delete_job(self):
        """
        This function gets unplayed movies and TV shows and deletes them if they are eligible for deletion.
        """
        logger.debug("[JOB] Fetch and delete job started")

        if self.radarr_enabled:
            logger.debug("[JOB] Fetching and deleting movies")
            self.get_and_delete_movies()
        
        if self.sonarr_enabled:
            logger.debug("[JOB] Fetching and deleting series")
            self.get_and_delete_series()

        logger.debug("[JOB] Fetch and delete job finished")

    # def dynamic_load_job(self):
    #     """
    #     This function dynamically loads and unloads the Plex library based on the current time.
    #     """
    #     print("DYNAMIC LOAD JOB :: Starting")

    #     episodes_count = self.fetch_and_load_episodes()
    #     if self.config.dry_run and episodes_count > 0:
    #         print("DYNAMIC LOAD JOB :: DRY RUN :: Would have loaded " + str(episodes_count) + " episodes")
    #     elif episodes_count > 0:
    #         print("DYNAMIC LOAD JOB :: Loaded " + str(episodes_count) + " episodes")

    #     print("DYNAMIC LOAD JOB :: Finished")
    
    # def fetch_and_load_episodes(self):
    #     series = self.plex.get_currently_playing()
    #     for show in series:
    #         self.sonarr.find_and_load_episodes(show.tvdb_id, show.season, show.episode)

    #     return 0
            

    def get_and_delete_movies(self):
        """
        Fetches unplayed movies and deletes them if they are eligible for deletion.
        """
        media = self.plex.get_expired_media("movie", self.radarr_watched_deletion_threshold, self.radarr_unwatched_deletion_threshold)

        media_to_delete = {}
        for item in media:
            tmdb_id = next(
                (guid.id.split("tmdb://")[1].split("?")[0] for guid in item.guids if guid.id.startswith("tmdb://")),
                None,
            )
            if tmdb_id is not None:
                media_to_delete[tmdb_id] = item.title

        media_deleted = self.radarr.get_and_delete_media(media_to_delete, self.dry_run)
        if self.overseerr_enabled:
            self.overseerr.get_and_delete_media(media_deleted, self.dry_run)

    def get_and_delete_series(self):
        """
        Fetches unplayed TV shows and deletes them if they are eligible for deletion.
        """
        media = self.plex.get_expired_media("show", self.sonarr_watched_deletion_threshold, self.sonarr_unwatched_deletion_threshold)

        media_to_delete = {}
        for item in media:
            tvdb_id = next(
                (guid.id.split("tvdb://")[1].split("?")[0] for guid in item.guids if guid.id.startswith("tvdb://")),
                None,
            )
            if tvdb_id is not None:
                media_to_delete[tvdb_id] = item.title

        media_deleted = self.sonarr.get_and_delete_media(media_to_delete, self.dry_run)
        if self.overseerr_enabled:
            self.overseerr.get_and_delete_media(media_deleted, self.dry_run)
