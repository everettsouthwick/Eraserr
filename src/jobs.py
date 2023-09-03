"""
This module contains the JobRunner class, 
which is responsible for running the job function on a schedule.
"""
from datetime import datetime
from typing import Optional
import time
import schedule
import requests
from src.overseerr import OverseerrClient
from src.plex import PlexClient
from src.radarr import RadarrClient
from src.sonarr import SonarrClient
from src.util import convert_bytes
from src.models.plex.plexmovie import PlexMovie
from src.models.plex.plexseries import PlexSeries
from src.models.radarr.radarrmovie import RadarrMovie
from src.models.sonarr.sonarrseries import SonarrSeries

class JobRunner:
    """
    Class for running the job function on a schedule.
    """
    def __init__(self, config):
        self.config = config
        self.overseerr = OverseerrClient(config)
        self.plex = PlexClient(config)
        self.radarr = RadarrClient(config)
        self.sonarr = SonarrClient(config)
        self.dynamic_load = config.sonarr.dynamic_load

    def run(self):
        """
        Runs the job function on a schedule.
        """
        if self.dynamic_load.enabled:
            self.dynamic_load_job()
            schedule.every(self.dynamic_load.schedule_interval).seconds.do(self.dynamic_load_job)

        self.fetch_and_delete_job()
        schedule.every(self.config.schedule_interval).seconds.do(self.fetch_and_delete_job)
        


        while True:
            schedule.run_pending()
            time.sleep(1)

    def fetch_and_delete_job(self):
        """
        This function fetches unplayed movies and TV shows and deletes them if they are eligible for deletion.
        """
        print("FETCH AND DELETE JOB :: Starting")

        total_size = self.fetch_and_delete_movies()
        if self.config.dry_run:
            print("FETCH AND DELETE JOB :: DRY RUN :: Would have freed up from movies: " + str(total_size))
        else:
            print("FETCH AND DELETE JOB :: Total freed up from movies: " + str(total_size))

        total_size = self.fetch_and_delete_series()
        if self.config.dry_run:
            print("FETCH AND DELETE JOB :: DRY RUN :: Would have freed up from series: " + str(total_size))
        else:
            print("FETCH AND DELETE JOB :: Total freed up from series: " + str(total_size))

        print("FETCH AND DELETE JOB :: Finished")

    def dynamic_load_job(self):
        """
        This function dynamically loads and unloads the Plex library based on the current time.
        """
        print("DYNAMIC LOAD JOB :: Starting")

        episodes_count = self.fetch_and_load_episodes()
        if self.config.dry_run:
            print("DYNAMIC LOAD JOB :: DRY RUN :: Would have loaded " + str(episodes_count) + " episodes")
        else:
            print("DYNAMIC LOAD JOB :: Loaded " + str(episodes_count) + " episodes")

        print("DYNAMIC LOAD JOB :: Finished")        
    
    def fetch_and_load_episodes(self):
        series = self.plex.get_currently_playing()
        for show in series:
            self.sonarr.find_and_load_episodes(show.tvdb_id, show.season, show.episode)

        return 0
            
    
    def should_delete_movie(self, plex_movie: PlexMovie, radarr_movie: Optional[RadarrMovie]):
        """
        Determines whether a movie should be deleted.
        
        Args:
            plex_movie (PlexMovie): The Plex movie to check.
            radarr_movie (Optional[RadarrMovie]): The Radarr movie to check.
            
        Returns:
            bool: Whether the movie should be deleted.
        """
        if radarr_movie is not None and radarr_movie.exempt:
            return False

        last_watched_threshold = datetime.fromtimestamp(
            time.time() - self.config.last_watched_days_deletion_threshold * 24 * 60 * 60
        )
        unwatched_threshold = datetime.fromtimestamp(
            time.time() - self.config.unwatched_days_deletion_threshold * 24 * 60 * 60
        )

        if plex_movie.unwatched and plex_movie.added_at is not None and plex_movie.added_at < unwatched_threshold:
            return True

        if (
            not plex_movie.unwatched
            and plex_movie.added_at is not None
            and plex_movie.last_watched_date is not None
            and plex_movie.added_at < last_watched_threshold
            and plex_movie.last_watched_date < last_watched_threshold
        ):
            return True

        return False

    def should_delete_series(self, plex_series: PlexSeries, sonarr_series: Optional[SonarrSeries]):
        """
        Determines whether a TV show should be deleted.
        
        Args:
            plex_series (PlexSeries): The Plex series to check.
            sonarr_series (Optional[SonarrSeries]): The Sonarr series to check.
        
        Returns:
            bool: Whether the TV show should be deleted.
        """
        if sonarr_series is not None and sonarr_series.exempt:
            return False
        
        last_watched_threshold = datetime.fromtimestamp(
            time.time() - self.config.last_watched_days_deletion_threshold * 24 * 60 * 60
        )
        unwatched_threshold = datetime.fromtimestamp(
            time.time() - self.config.unwatched_days_deletion_threshold * 24 * 60 * 60
        )

        if plex_series.unwatched and plex_series.added_at is not None and plex_series.added_at < unwatched_threshold:
            return True
        
        if (
            not plex_series.unwatched
            and plex_series.added_at is not None
            and plex_series.last_watched_date is not None
            and plex_series.added_at < last_watched_threshold
            and plex_series.last_watched_date < last_watched_threshold
        ):
            return True

        return False

    def fetch_and_delete_movies(self):
        """
        Fetches unplayed movies and deletes them if they are eligible for deletion.
        """
        all_tmdb_ids = []

        plex_movies = self.plex.get_movies()
        radarr_movies = self.radarr.get_movies()

        radarr_movies_dict_by_id = {movie.tmdb_id: movie for movie in radarr_movies}
        radarr_movies_dict_by_path = {movie.path: movie for movie in radarr_movies}

        for plex_movie in plex_movies:
            radarr_movie = radarr_movies_dict_by_id.get(plex_movie.tmdb_id)
            if radarr_movie is None:
                radarr_movie = radarr_movies_dict_by_path.get(plex_movie.path)

            if self.should_delete_movie(plex_movie, radarr_movie):
                if plex_movie.tmdb_id is not None:
                    all_tmdb_ids.append(plex_movie.tmdb_id)
                elif radarr_movie is not None and radarr_movie.tmdb_id is not None:
                    all_tmdb_ids.append(radarr_movie.tmdb_id)

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
            time.sleep(10)
            self.plex.find_and_update_library("movie")
        else:
            print("PLEX :: Skipping Plex library refresh")

        return str(convert_bytes(total_size))

    def fetch_and_delete_series(self):
        """
        Fetches unplayed TV shows and deletes them if they are eligible for deletion.
        """
        all_tvdb_ids = []

        plex_series = self.plex.get_series()
        sonarr_series = self.sonarr.get_series()

        sonarr_series_dict_by_id = {series.tvdb_id: series for series in sonarr_series}
        sonarr_series_dict_by_path = {series.path: series for series in sonarr_series}

        for plex_show in plex_series:
            sonarr_series = sonarr_series_dict_by_id.get(plex_show.tvdb_id)
            if sonarr_series is None:
                sonarr_series = sonarr_series_dict_by_path.get(plex_show.path)

            if self.should_delete_series(plex_show, sonarr_series):
                if plex_show.tvdb_id is not None:
                    all_tvdb_ids.append(plex_show.tvdb_id)
                elif sonarr_series is not None and sonarr_series.tvdb_id is not None:
                    all_tvdb_ids.append(sonarr_series.tvdb_id)

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
            time.sleep(10)
            self.plex.find_and_update_library("show")
        else:
            print("PLEX :: Skipping Plex library refresh")

        return str(convert_bytes(total_size))
