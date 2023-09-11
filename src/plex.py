"""Module for interacting with Plex."""
import os
import time
from datetime import datetime, timedelta
from plexapi.server import PlexServer
from src.models.plex.plexmovie import PlexMovie
from src.models.plex.plexseries import PlexSeries


class PlexClient:
    """Client for interacting with Plex."""

    def __init__(self, config):
        self.config = config
        self.base_url = config.plex.base_url
        self.token = config.plex.token
        self.refresh = config.plex.refresh
        self.plex = PlexServer(self.base_url, self.token)

    def get_movies(self, section_type="movie"):
        """
        Retrieves a list of movies from the specified section type.

        Args:
            section_type (str): The type of section to retrieve movies from.

        Returns:
            List[PlexMovie]: A list of PlexMovie objects representing the movies in the specified section.
        """
        movie_list = []

        sections = self.get_sections(section_type)
        for section in sections:
            for movie in section.all():
                movie_obj = self.parse_movie(movie)
                movie_list.append(movie_obj)

        return movie_list

    def parse_movie(self, movie):
        """
        Parses a Plex movie object into a PlexMovie object.

        Args:
            movie (plexapi.video.Movie): The Plex movie object to parse.

        Returns:
            PlexMovie: A PlexMovie object representing the movie.
        """
        tmdb_id = next(
            (guid.id.split("tmdb://")[1].split("?")[0] for guid in movie.guids if guid.id.startswith("tmdb://")),
            None,
        )
        imdb_id = next(
            (guid.id.split("imdb://")[1].split("?")[0] for guid in movie.guids if guid.id.startswith("imdb://")),
            None,
        )
        path = movie.media[0].parts[0].file
        if path:
            path = os.path.dirname(path)
        title = movie.title
        # Set it to 1970-01-01 if the movie was added before Plex started tracking that data
        added_at = movie.addedAt if movie.addedAt else datetime.fromtimestamp(0)
        min_date = datetime.now() - timedelta(seconds=self.config.last_watched_deletion_threshold)
        history = self.plex._server.history(mindate=min_date, ratingKey=movie.ratingKey)
        last_watched_date = max(entry.viewedAt for entry in history) if history else None

        movie_obj = PlexMovie(tmdb_id, imdb_id, path, title, added_at, last_watched_date)

        return movie_obj

    def get_series(self, section_type="show"):
        """
        Retrieves a list of TV series from the specified section type.

        Args:
            section_type (str): The type of section to retrieve TV series from.

        Returns:
            List[PlexSeries]: A list of PlexSeries objects representing the TV series in the specified section.
        """
        series_list = []

        sections = self.get_sections(section_type)
        for section in sections:
            for series in section.all():
                series_obj = self.parse_series(series)
                series_list.append(series_obj)

        return series_list

    def parse_series(self, series, season=None, episode=None):
        """
        Parses a Plex series object into a PlexSeries object.

        Args:
            series (plexapi.video.Show): The Plex series object to parse.

        Returns:
            PlexSeries: A PlexSeries object representing the series.
        """
        tvdb_id = next(
            (guid.id.split("tvdb://")[1].split("?")[0] for guid in series.guids if guid.id.startswith("tvdb://")),
            None,
        )
        imdb_id = next(
            (guid.id.split("imdb://")[1].split("?")[0] for guid in series.guids if guid.id.startswith("imdb://")),
            None,
        )
        path = series.episodes()[0].media[0].parts[0].file

        if path:
            # Get the season directory
            path = os.path.dirname(path)
            # Get the series directory
            path = os.path.dirname(path)
        title = series.title
        added_at = series.addedAt if series.addedAt else datetime.fromtimestamp(0)
        added_at = max(episode.addedAt for episode in series.episodes()) if series.episodes() else added_at
        min_date = datetime.now() - timedelta(seconds=self.config.last_watched_deletion_threshold)
        history = self.plex._server.history(mindate=min_date, ratingKey=series.ratingKey)
        last_watched_date = max(entry.viewedAt for entry in history) if history else None

        series_obj = PlexSeries(tvdb_id, imdb_id, path, title, added_at, last_watched_date, season, episode)

        return series_obj

    def get_sections(self, section_type):
        """
        Retrieves the section IDs for a given section type.

        Args:
            section_type (str): The type of section to retrieve.

        Returns:
            List[int]: A list of section IDs.
        """
        sections = []

        for section in self.plex.library.sections():
            if section.type == section_type:
                sections.append(section)

        return sections

    def update_library(self, section):
        """
        Updates the given section.

        Args:
            section (plexapi.library.LibrarySection): The section to update.
        """
        section.update()

    def find_and_update_library(self, section_type):
        """
        Finds and updates the given section type.

        Args:
            section_type (str): The type of section to update.
        """
        sections = self.get_sections(section_type)

        for section in sections:
            self.update_library(section)
            refreshing = self.plex.library.sectionByID(section.key).refreshing
            sleep_time = 30
            max_refresh_time = 600

            while refreshing and max_refresh_time > 0:
                refreshing = self.plex.library.sectionByID(section.key).refreshing
                print(f"PLEX :: Waiting for {section.title} to finish updating...")
                max_refresh_time -= sleep_time
                time.sleep(sleep_time)

        print(f"PLEX :: Updated {len(sections)} Plex {section_type} library")

    def get_currently_playing(self):
        """
        Retrieves a list of currently playing TV series.

        Returns:
            List[PlexSeries]: A list of PlexSeries objects representing the currently playing TV series.
        """
        series = []
        sessions = self.plex._server.sessions()
        for session in sessions:
            if not session.type == "episode":
                continue

            series_guid = session.grandparentGuid
            sections = self.get_sections("show")
            for section in sections:
                show = section.getGuid(series_guid)
                if show:
                    parsed_series = self.parse_series(show, session.parentIndex, session.index)
                    series.append(parsed_series)
                    break
        
        return series
    
