class PlexSeries:
    def __init__(self, tvdb_id, imdb_id, path, title, added_at, last_watched_date):
        self.tvdb_id = tvdb_id
        self.imdb_id = imdb_id
        self.path = path
        self.title = title
        self.added_at = added_at
        self.last_watched_date = last_watched_date if last_watched_date else None
        self.unwatched = bool(last_watched_date is None)
