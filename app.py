from tautulli import fetch_libraries, fetch_and_count_unplayed_titles, refresh_library
from radarr import find_and_delete_movie
from sonarr import find_and_delete_series
from overseerr import find_and_delete_media
from plex import find_and_update_library
import os
from dotenv import load_dotenv
from util import convert_bytes
import schedule
import time


load_dotenv()

DRY_RUN = os.getenv("DRY_RUN", "False").lower() in ("true", "1", "t")
DEFAULT_SCHEDULE_INTERVAL = "86400"
SCHEDULE_INTERVAL = int(os.getenv("SCHEDULE_INTERVAL", DEFAULT_SCHEDULE_INTERVAL))


def job():
    """
    This function fetches unplayed movies and TV shows and deletes them if they are eligible for deletion.
    """
    print("JOB :: Starting")

    # total_size = fetch_movies()
    # if DRY_RUN:
    #     print("JOB :: DRY RUN :: Would have freed up from movies: " + str(total_size))
    # else:
    #    print("JOB :: Total freed up from movies: " + str(total_size))

    total_size = fetch_series()
    if DRY_RUN:
        print("JOB :: DRY RUN :: Would have freed up from series: " + str(total_size))
    else:
        print("JOB :: Total freed up from series: " + str(total_size))

    print("JOB :: Finished")


def fetch_movies():
    """
    Fetches unplayed movies and deletes them if they are eligible for deletion.
    """
    section_ids = fetch_libraries("movie")
    all_tmdb_ids = fetch_and_count_unplayed_titles(section_ids)

    total_size = 0
    for tmdb_id in all_tmdb_ids:
        try:
            size = find_and_delete_movie(tmdb_id)
            if size is not None:
                total_size += size
            find_and_delete_media(tmdb_id)
        except Exception as ex:
            print(f"Error: {ex}")
            continue
    find_and_update_library("movie")
    refresh_library(section_ids, "movie")

    return str(convert_bytes(total_size))


def fetch_series():
    """
    Fetches unplayed TV shows and deletes them if they are eligible for deletion.
    """
    section_ids = fetch_libraries("show")
    all_tvdb_ids = fetch_and_count_unplayed_titles(section_ids)

    total_size = 0
    for tvdb_id in all_tvdb_ids:
        try:
            size = find_and_delete_series(tvdb_id)
            if size is not None:
                total_size += size
            find_and_delete_media(tvdb_id)
        except Exception as ex:
            print(f"Error: {ex}")
            continue
    find_and_update_library("show")
    refresh_library(section_ids, "show")

    return str(convert_bytes(total_size))


# Run the job function immediately on first execution
job()

# Then schedule it to run subsequently every SCHEDULE_INTERVAL seconds
schedule.every(SCHEDULE_INTERVAL).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
