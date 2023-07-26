import json
import sys
from typing import Any, Dict, List
from dataclasses import dataclass, field

CONFIG_FILE_NAME = "config.json"


@dataclass
class TautulliConfig:
    api_key: str
    base_url: str
    fetch_limit: int


@dataclass
class RadarrConfig:
    api_key: str
    base_url: str
    exempt_tag_names: List[str] = field(default_factory=list)


@dataclass
class SonarrConfig:
    api_key: str
    base_url: str
    monitor_continuing_series: bool
    exempt_tag_names: List[str] = field(default_factory=list)


@dataclass
class OverseerrConfig:
    api_key: str
    base_url: str
    fetch_limit: int


@dataclass
class PlexConfig:
    base_url: str
    token: str
    refresh: bool


@dataclass
class Config:
    tautulli: TautulliConfig
    radarr: RadarrConfig
    sonarr: SonarrConfig
    overseerr: OverseerrConfig
    plex: PlexConfig
    last_watched_days_deletion_threshold: int
    unwatched_days_deletion_threshold: int
    dry_run: bool
    schedule_interval: int

    def __init__(self):
        # Default values are set
        self.tautulli = TautulliConfig("", "http://host:port/api/v2", 25)
        self.radarr = RadarrConfig("", "http://host:port/api/v3", [])
        self.sonarr = SonarrConfig("", "http://host:port/api/v3", True, [])
        self.overseerr = OverseerrConfig("", "http://host:port/api/v1", 10)
        self.plex = PlexConfig("http://host:port", "", True)
        self.last_watched_days_deletion_threshold = 90
        self.unwatched_days_deletion_threshold = 30
        self.dry_run = True
        self.schedule_interval = 86400

        # Read the config file
        config = self._get_config()

        # Set the configuration values if provided
        try:
            self._parse_config(config)
        except TypeError as err:
            print("Error in configuration file:")
            print(err)
            sys.exit()

    def _get_config(self) -> Dict[str, Any]:
        """
        Reads the configuration file and returns its contents as a dictionary.

        Returns:
            A dictionary containing the configuration values.
        """
        config = {}
        try:
            with open(CONFIG_FILE_NAME, encoding="utf-8") as file:
                config = json.load(file)
        except FileNotFoundError:
            pass

        return config

    def _parse_config(self, config: Dict[str, Any]) -> None:
        """
        Parses the configuration dictionary and sets the corresponding attributes of the Config object.

        Args:
            config: A dictionary containing the configuration values.

        Raises:
            TypeError: If any of the configuration values are of the wrong type.
            ValueError: If any of the configuration values are invalid.
        """
        if "tautulli" in config:
            self.tautulli = TautulliConfig(**config["tautulli"])
        if "radarr" in config:
            self.radarr = RadarrConfig(**config["radarr"])
        if "sonarr" in config:
            self.sonarr = SonarrConfig(**config["sonarr"])
        if "overseerr" in config:
            self.overseerr = OverseerrConfig(**config["overseerr"])
        if "plex" in config:
            self.plex = PlexConfig(**config["plex"])
        if "last_watched_days_deletion_threshold" in config:
            self.last_watched_days_deletion_threshold = config["last_watched_days_deletion_threshold"]
        if "unwatched_days_deletion_threshold" in config:
            self.unwatched_days_deletion_threshold = config["unwatched_days_deletion_threshold"]
        if "dry_run" in config:
            self.dry_run = config["dry_run"] in [True, "True", "true", "1"]
        if "schedule_interval" in config:
            self.schedule_interval = config["schedule_interval"]
