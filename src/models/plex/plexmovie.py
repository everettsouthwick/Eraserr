class PlexMovie:
    def __init__(self, title, added_at, last_watched_date, tmdbid):
        self.title = title
        self.added_at = added_at
        self.last_watched_date = last_watched_date if last_watched_date else None
        self.tmdbid = tmdbid
        self.unwatched = bool(last_watched_date is None)
