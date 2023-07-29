class PlexSeries:
    def __init__(self, title, added_at, last_watched_date, tvdbid):
        self.title = title
        self.added_at = added_at
        self.last_watched_date = last_watched_date if last_watched_date else None
        self.tvdbid = tvdbid
        self.unwatched = bool(last_watched_date is None)
