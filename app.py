from tautulli import fetch_and_count_unplayed_titles
from radarr import find_and_delete_movie
from sonarr import find_and_delete_series
from overseerr import find_and_delete_request
from dotenv import load_dotenv
from util import convert_bytes
import os

load_dotenv()

DRY_RUN = os.getenv("DRY_RUN", 'False').lower() in ('true', '1', 't')
MOVIE_SECTION_ID = os.getenv("TAUTULLI_MOVIE_SECTION_ID")
TV_SECTION_ID = os.getenv("TAUTULLI_TV_SECTION_ID")

def fetch_movies():
    """
    Fetches unplayed movies and deletes them if they are eligible for deletion.
    """
    count, tmdb_ids = fetch_and_count_unplayed_titles(MOVIE_SECTION_ID)
    print(f"There are {count} movies eligible for deletion. TMDB IDs: {tmdb_ids}")
    total_size = 0
    if not DRY_RUN:
        for tmdb_id in tmdb_ids:
            try:
                total_size += find_and_delete_movie(tmdb_id)
                find_and_delete_request(tmdb_id)
            except Exception as ex:
                print(f"Error: {ex}")
                continue
    else:
        print("Dry run set to true. Skipping deletion process")

    print('Total freed up from movies: ' + convert_bytes(total_size))

def fetch_series():
    """
    Fetches unplayed TV shows and deletes them if they are eligible for deletion.
    """
    count, tvdb_ids = fetch_and_count_unplayed_titles(TV_SECTION_ID)
    print(f"There are {count} tv shows eligible for deletion. TVDB IDs: {tvdb_ids}")
    total_size = 0
    if not DRY_RUN:
        for tvdb_id in tvdb_ids:
            try:
                total_size += find_and_delete_series(tvdb_id)
                find_and_delete_request(tvdb_id)
            except Exception as ex:
                print(f"Error: {ex}")
                continue
    else:
        print("Dry run set to true. Skipping deletion process")

    print('Total freed up from series: ' + convert_bytes(total_size))

fetch_movies()
fetch_series()