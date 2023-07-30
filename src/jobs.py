import time
from typing import Optional
import schedule
import requests
from datetime import datetime
from src.overseerr import OverseerrClient
from src.plex import PlexClient
from src.radarr import RadarrClient
from src.sonarr import SonarrClient
from src.util import convert_bytes
from src.models.plex.plexmovie import PlexMovie
from src.models.plex.plexseries import PlexSeries
from src.models.radarr.radarrmovie import RadarrMovie


class JobRunner:
    def __init__(self, config):
        self.config = config
        self.overseerr = OverseerrClient(config)
        self.plex = PlexClient(config)
        self.radarr = RadarrClient(config)
        self.sonarr = SonarrClient(config)

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

    def should_delete_movie(self, plex_movie: PlexMovie, radarr_movie: Optional[RadarrMovie]):
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

    def should_delete_series(self, series: PlexSeries):
        last_watched_threshold = datetime.fromtimestamp(
            time.time() - self.config.last_watched_days_deletion_threshold * 24 * 60 * 60
        )
        unwatched_threshold = datetime.fromtimestamp(
            time.time() - self.config.unwatched_days_deletion_threshold * 24 * 60 * 60
        )

        if series.tvdb_id is None:
            return False

        if series.unwatched and series.added_at is not None and series.added_at < unwatched_threshold:
            return True

        if (
            not series.unwatched
            and series.added_at is not None
            and series.last_watched_date is not None
            and series.added_at < last_watched_threshold
            and series.last_watched_date < last_watched_threshold
        ):
            return True

        return False

    def fetch_movies(self):
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

    def fetch_series(self):
        """
        Fetches unplayed TV shows and deletes them if they are eligible for deletion.
        """
        all_tvdb_ids = []

        series = self.plex.get_series()
        for show in series:
            if self.should_delete_series(show):
                all_tvdb_ids.append(show.tvdb_id)

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
