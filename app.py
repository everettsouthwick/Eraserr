from tautulli import fetch_and_count_unplayed_titles
from radarr import get_radarr_id, delete_unplayed_movie
from sonarr import get_sonarr_id, delete_unplayed_series
from overseerr import find_and_delete_request

def fetch_movies():
    count, total_size, tmdb_ids = fetch_and_count_unplayed_titles(1)
    print(f"There are {count} movies eligible for deletion. Deletion would save {total_size}. TMDB IDs: {tmdb_ids}")
    for tmdb_id in tmdb_ids:
        radarr_id = get_radarr_id(tmdb_id)
        if radarr_id:
            delete_unplayed_movie(radarr_id)
            find_and_delete_request(tmdb_id)

def fetch_tv_shows():
    count, total_size, tvdb_ids = fetch_and_count_unplayed_titles(2)
    print(f"There are {count} tv shows eligible for deletion. Deletion would save {total_size}. TVDB IDs: {tvdb_ids}")
    for tvdb_id in tvdb_ids:
        sonarr_id = get_sonarr_id(tvdb_id)
        if sonarr_id:
            delete_unplayed_series(sonarr_id)
            find_and_delete_request(tvdb_id)

fetch_movies()
fetch_tv_shows()
