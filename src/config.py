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
class ProgressiveDeletion:
    """This class is used to store the configuration values for the progressive deletion feature."""
    enabled: bool
    maximum_deletion_cycles: int
    threshold_reduction_per_cycle: int

@dataclass
class FreeSpace:
    """This class is used to store the configuration values for the free space feature."""
    enabled: bool
    minimum_free_space_percentage: int
    path: str
    prevent_age_based_deletion: bool
    prevent_dynamic_load: bool
    progressive_deletion: field(default_factory=ProgressiveDeletion)


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
        self.experimental = Experimental(FreeSpace(False, 0, "", False, False, ProgressiveDeletion(False, 0, 86400)))
        
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
            plex_config = config.get("plex", {})
            self.plex = PlexConfig(plex_config.get("base_url", "https://host:port"), plex_config.get("token", ""))
            radarr_config = config.get("radarr", {})
            self.radarr = RadarrConfig(radarr_config.get("enabled", False), radarr_config.get("api_key", ""), radarr_config.get("base_url", "https://host:port/api/v3"), radarr_config.get("exempt_tag_names", []), radarr_config.get("watched_deletion_threshold", 7776000), radarr_config.get("unwatched_deletion_threshold", 2592000))
            self.radarr.watched_deletion_threshold = self._convert_to_seconds(self.radarr.watched_deletion_threshold, "radarr.watched_deletion_threshold")
            self.radarr.unwatched_deletion_threshold = self._convert_to_seconds(self.radarr.unwatched_deletion_threshold, "radarr.unwatched_deletion_threshold")
            sonarr_config = config.get("sonarr", {})
            dynamic_load_config = sonarr_config.get("dynamic_load", {})
            self.sonarr = SonarrConfig(sonarr_config.get("enabled", False), sonarr_config.get("api_key", ""), sonarr_config.get("base_url", "https://host:port/api/v3"), sonarr_config.get("monitor_continuing_series", True), sonarr_config.get("exempt_tag_names", []), DynamicLoad(dynamic_load_config.get("enabled", False), dynamic_load_config.get("episodes_to_load", 3), dynamic_load_config.get("episodes_to_keep", 3), dynamic_load_config.get("watched_deletion_threshold", 7776000), dynamic_load_config.get("schedule_interval", 600)), sonarr_config.get("watched_deletion_threshold", 7776000), sonarr_config.get("unwatched_deletion_threshold", 2592000))
            self.sonarr.dynamic_load.schedule_interval = self._convert_to_seconds(self.sonarr.dynamic_load.schedule_interval, "sonarr.dynamic_load.schedule_interval")
            self.sonarr.dynamic_load.watched_deletion_threshold = self._convert_to_seconds(self.sonarr.dynamic_load.watched_deletion_threshold, "sonarr.dynamic_load.watched_deletion_threshold")
            self.sonarr.watched_deletion_threshold = self._convert_to_seconds(self.sonarr.watched_deletion_threshold, "sonarr.watched_deletion_threshold")
            self.sonarr.unwatched_deletion_threshold = self._convert_to_seconds(self.sonarr.unwatched_deletion_threshold, "sonarr.unwatched_deletion_threshold")
            overseerr_config = config.get("overseerr", {})
            self.overseerr = OverseerrConfig(overseerr_config.get("enabled", False), overseerr_config.get("api_key", ""), overseerr_config.get("base_url", "http://host:port/api/v1"), overseerr_config.get("fetch_limit", 10))
            experimental_config = config.get("experimental", {})
            free_space_config = experimental_config.get("free_space", {})
            progressive_deletion_config = free_space_config.get("progressive_deletion", {})
            self.experimental = Experimental(FreeSpace(free_space_config.get("enabled", False), free_space_config.get("minimum_free_space_percentage", 0), free_space_config.get("path", ""), free_space_config.get("prevent_age_based_deletion", False), free_space_config.get("prevent_dynamic_load", False), ProgressiveDeletion(progressive_deletion_config.get("enabled", False), progressive_deletion_config.get("maximum_deletion_cycles", 0), progressive_deletion_config.get("threshold_reduction_per_cycle", 86400))))
            self.experimental.free_space.progressive_deletion.threshold_reduction_per_cycle = self._convert_to_seconds(self.experimental.free_space.progressive_deletion.threshold_reduction_per_cycle, "experimental.free_space.progressive_deletion.threshold_reduction_per_cycle")
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
            return value