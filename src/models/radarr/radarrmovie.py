class RadarrMovie:
    def __init__(self, tmdb_id, imdb_id, path, title, movie_file_id, tags, exempt):
        self.tmdb_id = tmdb_id
        self.imdb_id = imdb_id
        self.path = path
        self.title = title
        self.movie_file_id = movie_file_id
        self.tags = tags
        self.exempt = exempt
