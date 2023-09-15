"""This module contains the Config class which is used to store the configuration values for the application."""
import json
import sys
import re
from typing import Any, Dict, List
from dataclasses import dataclass, field

CONFIG_FILE_NAME = "config.json"

@dataclass
class PlexConfig:
    """This class is used to store the configuration values for the Plex client."""
    base_url: str
    token: str

@dataclass
class RadarrConfig:
    """This class is used to store the configuration values for the Radarr client."""
    enabled: bool
    api_key: str
    base_url: str
    exempt_tag_names: List[str] = field(default_factory=list)
    watched_deletion_threshold: int = 7776000
    unwatched_deletion_threshold: int = 2592000

@dataclass
class DynamicLoad:
    """This class is used to store the configuration values for the dynamic load feature."""
    enabled: bool
    episodes_to_load: int
    episodes_to_keep: int
    watched_deletion_threshold: int = 7776000
    schedule_interval: int = 600

@dataclass
class SonarrConfig:
    """This class is used to store the configuration values for the Sonarr client."""
    enabled: bool
    api_key: str
    base_url: str
    monitor_continuing_series: bool
    exempt_tag_names: List[str] = field(default_factory=list)
    dynamic_load: DynamicLoad = field(default_factory=DynamicLoad)
    watched_deletion_threshold: int = 7776000
    unwatched_deletion_threshold: int = 2592000

@dataclass
class OverseerrConfig:
    """This class is used to store the configuration values for the Overseerr client."""
    enabled: bool
    api_key: str
    base_url: str
    fetch_limit: int

@dataclass
class FreeSpace:
    """This class is used to store the configuration values for the free space feature."""
    enabled: bool
    minimum_free_space_percentage: int
    path: str

@dataclass
class Experimental:
    """This class is used to store the configuration values for the experimental features."""
    free_space: FreeSpace = field(default_factory=FreeSpace)

@dataclass
class Config:
    """This class is used to store the configuration values for the application."""
    plex: PlexConfig
    radarr: RadarrConfig
    sonarr: SonarrConfig
    overseerr: OverseerrConfig
    dry_run: bool
    log_level: str
    schedule_interval: int = 86400
    

    def __init__(self):
        self.dry_run = True
        self.log_level = "INFO"
        self.schedule_interval = 86400
        self.plex = PlexConfig("https://host:port", "")
        self.radarr = RadarrConfig(False, "", "https://host:port/api/v3", [], 7776000, 2592000)
        self.sonarr = SonarrConfig(False, "", "https://host:port/api/v3", True, [], DynamicLoad(False, 3, 3, 7776000, 600), 7776000, 2592000)
        self.overseerr = OverseerrConfig(False, "", "http://host:port/api/v1", 10)
        self.experimental = Experimental(FreeSpace(False, "", 0))
        
        config = self._get_config()

        try:
            self._parse_config(config)
        except TypeError as err:
            print("Error in configuration file:")
            print(err)
            sys.exit()

    def _get_config(self) -> Dict[str, Any]:
        config = {}
        try:
            with open(CONFIG_FILE_NAME, encoding="utf-8") as file:
                config = json.load(file)
        except FileNotFoundError:
            pass

        return config

    def _parse_config(self, config: Dict[str, Any]) -> None:
        required_keys = [
            "dry_run",
            "log_level",
            "schedule_interval",
            "plex"        
        ]

        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required configuration key: {key}")

        try:
            self.dry_run = config.get("dry_run", True)
            self.log_level = config.get("log_level", "INFO")
            self.schedule_interval = self._convert_to_seconds(config.get("schedule_interval", "86400"), "schedule_interval")
            self.plex = PlexConfig(**config.get("plex", {"base_url": "", "token": ""}))
            self.radarr = RadarrConfig(**config.get("radarr", {"enabled": False, "api_key": "", "base_url": "", "exempt_tag_names": [], "watched_deletion_threshold": 7776000, "unwatched_deletion_threshold": 2592000}))
            self.sonarr = SonarrConfig(**config.get("sonarr", {"enabled": False, "api_key": "", "base_url": "", "monitor_continuing_series": True, "exempt_tag_names": [], "dynamic_load": {"enabled": False, "episodes_to_load": 3, "episodes_to_keep": 3, "watched_deletion_threshold": 7776000, "schedule_interval": 600}, "watched_deletion_threshold": 7776000, "unwatched_deletion_threshold": 2592000}))
            self.overseerr = OverseerrConfig(**config.get("overseerr", {"enabled": False, "api_key": "", "base_url": "", "fetch_limit": 10}))
            self.experimental = Experimental(**config.get("experimental", {"free_space": {"enabled": False, "minimum_free_space_percentage": 0, "path": ""}}))
        except ValueError as err:
            print("Error in configuration file:")
            print(err)
            sys.exit()
    
    def _convert_to_seconds(self, time: str, key_name: str) -> int:
        """
        Converts a time string to seconds.

        Args:
            time: A string representing a time interval in the format of <integer><unit>. (e.g. 45s (seconds), 30m (minutes), 2h (hours), 1d (days))

        Returns:
            An integer representing the time interval in seconds.

        Raises:
            ValueError: If the time string is not in the correct format or contains an invalid time unit.
        """
        # If the time is already an integer, return it
        try:
            return int(time)
        except ValueError:
            pass

        match = re.match(r'^(\d+)([smhd])$', time.lower())

        if not match:
            raise ValueError(f"{key_name} must be in the format of <integer><unit>. (e.g. 45s (seconds), 30m (minutes), 2h (hours), 1d (days))")
        
        value, unit = int(match.group(1)), match.group(2)

        if unit == "s":
            return value
        elif unit == "m":
            return value * 60
        elif unit == "h":
            return value * 3600
        elif unit == "d":
            return value * 86400
        else:
            raise ValueError(f"'retrieval_interval' invalid time unit: {unit}. Accepted units: s (seconds), m (minutes), h (hours), d (days).")