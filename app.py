from tautulli import fetch_and_count_unplayed_titles
from radarr import find_and_delete_movie
from sonarr import find_and_delete_series
from overseerr import find_and_delete_request
from dotenv import load_dotenv
import os

load_dotenv()

DRY_RUN = os.getenv("DRY_RUN", 'False').lower() in ('true', '1', 't')

def fetch_movies():
    """
    Fetches unplayed movies and deletes them if they are eligible for deletion.
    """
    count, total_size, tmdb_ids = fetch_and_count_unplayed_titles(1)
    print(f"There are {count} movies eligible for deletion. Deletion would save {total_size}. TMDB IDs: {tmdb_ids}")
    if not DRY_RUN:
        for tmdb_id in tmdb_ids:
            try:
                find_and_delete_movie(tmdb_id)
                find_and_delete_request(tmdb_id)
            except Exception as ex:
                print(f"Error: {ex}")
                continue
    else:
        print("Dry run set to true. Skipping deletion process")

def fetch_tv_shows():
    """
    Fetches unplayed TV shows and deletes them if they are eligible for deletion.
    """
    count, total_size, tvdb_ids = fetch_and_count_unplayed_titles(2)
    print(f"There are {count} tv shows eligible for deletion. Deletion would save {total_size}. TVDB IDs: {tvdb_ids}")
    if not DRY_RUN:
        for tvdb_id in tvdb_ids:
            try:
                find_and_delete_series(tvdb_id)
                find_and_delete_request(tvdb_id)
            except Exception as ex:
                print(f"Error: {ex}")
                continue
    else:
        print("Dry run set to true. Skipping deletion process")

fetch_movies()
fetch_tv_shows()