import time
import schedule
import requests
from src.overseerr import OverseerrClient
from src.plex import PlexClient
from src.radarr import RadarrClient
from src.sonarr import SonarrClient
from src.tautulli import TautulliClient
from src.util import convert_bytes


class JobRunner:
    def __init__(self, config):
        self.config = config
        self.overseerr = OverseerrClient(config)
        self.plex = PlexClient(config)
        self.radarr = RadarrClient(config)
        self.sonarr = SonarrClient(config)
        self.tautulli = TautulliClient(config)

    def run(self):
        # Run the job function immediately on first execution
        self.job()

        # Then schedule it to run subsequently every self.config.schedule_interval seconds
        schedule.every(self.config.schedule_interval).seconds.do(self.job)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def job(self):
        """
        This function fetches unplayed movies and TV shows and deletes them if they are eligible for deletion.
        """
        print("JOB :: Starting")

        total_size = self.fetch_movies()
        if self.config.dry_run:
            print("JOB :: DRY RUN :: Would have freed up from movies: " + str(total_size))
        else:
            print("JOB :: Total freed up from movies: " + str(total_size))

        total_size = self.fetch_series()
        if self.config.dry_run:
            print("JOB :: DRY RUN :: Would have freed up from series: " + str(total_size))
        else:
            print("JOB :: Total freed up from series: " + str(total_size))

        print("JOB :: Finished")

    def fetch_movies(self):
        """
        Fetches unplayed movies and deletes them if they are eligible for deletion.
        """
        section_ids = self.tautulli.fetch_libraries("movie")
        all_tmdb_ids = self.tautulli.fetch_and_count_unplayed_titles(section_ids)

        total_size = 0
        for tmdb_id in all_tmdb_ids:
            try:
                deleted, size = self.radarr.find_and_delete_movie(tmdb_id)
                if deleted and size is not None:
                    total_size += size
                    self.overseerr.find_and_delete_media(tmdb_id)
            except requests.exceptions.RequestException as ex:
                print(f"Error: {ex}")
                continue
        if self.config.plex.refresh:
            self.plex.find_and_update_library("movie")
        else:
            print("PLEX :: Skipping Plex library refresh")
        self.tautulli.refresh_library(section_ids, "movie")

        return str(convert_bytes(total_size))

    def fetch_series(self):
        """
        Fetches unplayed TV shows and deletes them if they are eligible for deletion.
        """
        section_ids = self.tautulli.fetch_libraries("show")
        all_tvdb_ids = self.tautulli.fetch_and_count_unplayed_titles(section_ids)

        total_size = 0
        for tvdb_id in all_tvdb_ids:
            try:
                deleted, size = self.sonarr.find_and_delete_series(tvdb_id)
                if deleted and size is not None:
                    total_size += size
                    self.overseerr.find_and_delete_media(tvdb_id)
            except requests.exceptions.RequestException as ex:
                print(f"Error: {ex}")
                continue
        if self.config.plex.refresh:
            self.plex.find_and_update_library("show")
        else:
            print("PLEX :: Skipping Plex library refresh")
        self.tautulli.refresh_library(section_ids, "show")

        return str(convert_bytes(total_size))
