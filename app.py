from tautulli import fetch_libraries, fetch_and_count_unplayed_titles
from radarr import find_and_delete_movie
from sonarr import find_and_delete_series
from overseerr import find_and_delete_request
from dotenv import load_dotenv
from util import convert_bytes
import os
import schedule
import time

load_dotenv()

DRY_RUN = os.getenv("DRY_RUN", 'False').lower() in ('true', '1', 't')
DEFAULT_SCHEDULE_INTERVAL = 86400
SCHEDULE_INTERVAL = int(os.getenv("SCHEDULE_INTERVAL", DEFAULT_SCHEDULE_INTERVAL))

def job():
    """
    This function fetches unplayed movies and TV shows and deletes them if they are eligible for deletion.
    """
    print("Starting job")
    fetch_movies()
    fetch_series()
    print("Job finished")

def fetch_movies():
    """
    Fetches unplayed movies and deletes them if they are eligible for deletion.
    """
    total_count = 0
    all_tmdb_ids = []

    section_ids = fetch_libraries("movie")
    for section_id in section_ids:
        count, tmdb_ids = fetch_and_count_unplayed_titles(section_id)
        total_count += count
        all_tmdb_ids.extend(tmdb_ids)

    print(f"There are {total_count} movies eligible for deletion. TMDB IDs: {all_tmdb_ids}")
    total_size = 0
    if not DRY_RUN:
        for tmdb_id in all_tmdb_ids:
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
    total_count = 0
    all_tvdb_ids = []

    section_ids = fetch_libraries("show")
    for section_id in section_ids:
        count, tvdb_ids = fetch_and_count_unplayed_titles(section_id)
        total_count += count
        all_tvdb_ids.extend(tvdb_ids)

    print(f"There are {total_count} tv shows eligible for deletion. TVDB IDs: {all_tvdb_ids}")
    total_size = 0
    if not DRY_RUN:
        for tvdb_id in all_tvdb_ids:
            try:
                total_size += find_and_delete_series(tvdb_id)
                find_and_delete_request(tvdb_id)
            except Exception as ex:
                print(f"Error: {ex}")
                continue
    else:
        print("Dry run set to true. Skipping deletion process")

    print('Total freed up from series: ' + convert_bytes(total_size))

# Run the job function immediately on first execution
job()

# Then schedule it to run subsequently every SCHEDULE_INTERVAL seconds
schedule.every(SCHEDULE_INTERVAL).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)