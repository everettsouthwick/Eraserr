"""Module for DynamicMedia class."""
class DynamicMedia:
    """Class for representing dynamic media."""
    def __init__(self, media, unload: bool, season: int, episode: int):
        self.media = media
        self.unload = unload
        self.season = season
        self.episode = episode
