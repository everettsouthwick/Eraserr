class SonarrSeries:
    def __init__(self, tvdb_id, imdb_id, path, title, status, tags, exempt):
        self.tvdb_id = tvdb_id
        self.imdb_id = imdb_id
        self.path = path
        self.title = title
        self.status = status
        self.continuing = status == "continuing"
        self.tags = tags
        self.exempt = exempt
