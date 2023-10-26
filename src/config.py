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
        self.plex = PlexConfig("https://plex.domain.com", "")
        self.radarr = RadarrConfig(False, "", "https://radarr.domain.com/api/v3", [], 7776000, 2592000)
        self.sonarr = SonarrConfig(False, "", "https://sonarr.domain.com/api/v3", True, [], DynamicLoad(False, 3, 3, 7776000, 600), 7776000, 2592000)
        self.overseerr = OverseerrConfig(False, "", "https://overseerr.domain.com/api/v1", 10)
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
            self.dry_run = self._get_value_or_default(config, "dry_run", True)
            self.log_level = self._get_value_or_default(config, "log_level", "INFO")
            self.schedule_interval = self._get_value_or_default(config, "schedule_interval", 86400, True)
            plex_config = self._get_value_or_default(config, "plex", {})
            self.plex = PlexConfig(self._get_value_or_default(plex_config, "base_url", "https://plex.domain.com"), self._get_value_or_default(plex_config, "token", ""))
            radarr_config = self._get_value_or_default(config, "radarr", {})
            self.radarr = RadarrConfig(self._get_value_or_default(radarr_config, "enabled", False), self._get_value_or_default(radarr_config, "api_key", ""), self._get_value_or_default(radarr_config, "base_url", "https://radarr.domain.com/api/v3"), self._get_value_or_default(radarr_config, "exempt_tag_names", []), self._get_value_or_default(radarr_config, "watched_deletion_threshold", 7776000, True), self._get_value_or_default(radarr_config, "unwatched_deletion_threshold", 2592000, True))
            sonarr_config = self._get_value_or_default(config, "sonarr", {})
            dynamic_load_config = self._get_value_or_default(sonarr_config, "dynamic_load", {})
            self.sonarr = SonarrConfig(self._get_value_or_default(sonarr_config, "enabled", False), self._get_value_or_default(sonarr_config, "api_key", ""), self._get_value_or_default(sonarr_config, "base_url", "https://sonarr.domain.com/api/v3"), self._get_value_or_default(sonarr_config, "monitor_continuing_series", True), self._get_value_or_default(sonarr_config, "exempt_tag_names", []), DynamicLoad(self._get_value_or_default(dynamic_load_config, "enabled", False), self._get_value_or_default(dynamic_load_config, "episodes_to_load", 3), self._get_value_or_default(dynamic_load_config, "episodes_to_keep", 3), self._get_value_or_default(dynamic_load_config, "watched_deletion_threshold", 7776000, True), self._get_value_or_default(dynamic_load_config, "schedule_interval", 600, True)), self._get_value_or_default(sonarr_config, "watched_deletion_threshold", 7776000, True), self._get_value_or_default(sonarr_config, "unwatched_deletion_threshold", 2592000, True))
            overseerr_config = self._get_value_or_default(config, "overseerr", {})
            self.overseerr = OverseerrConfig(self._get_value_or_default(overseerr_config, "enabled", False), self._get_value_or_default(overseerr_config, "api_key", ""), self._get_value_or_default(overseerr_config, "base_url", "https://overseerr.domain.com/api/v1"), self._get_value_or_default(overseerr_config, "fetch_limit", 10))
            experimental_config = self._get_value_or_default(config, "experimental", {})
            free_space_config = self._get_value_or_default(experimental_config, "free_space", {})
            progressive_deletion_config = self._get_value_or_default(free_space_config, "progressive_deletion", {})
            self.experimental = Experimental(FreeSpace(self._get_value_or_default(free_space_config, "enabled", False), self._get_value_or_default(free_space_config, "minimum_free_space_percentage", 0), self._get_value_or_default(free_space_config, "path", ""), self._get_value_or_default(free_space_config, "prevent_age_based_deletion", False), self._get_value_or_default(free_space_config, "prevent_dynamic_load", False), ProgressiveDeletion(self._get_value_or_default(progressive_deletion_config, "enabled", False), self._get_value_or_default(progressive_deletion_config, "maximum_deletion_cycles", 0), self._get_value_or_default(progressive_deletion_config, "threshold_reduction_per_cycle", 86400, True))))
        except ValueError as err:
            print("Error in configuration file:")
            print(err)
            sys.exit()

    def _get_value_or_default(self, config: Dict[str, Any], key: str, default: Any, convert_to_seconds: bool = False) -> Any:
        if key not in config:
            print("Missing configuration key: %s. Using default value: %s", key, default)
            return default
        
        if convert_to_seconds:
            return self._convert_to_seconds(config.get(key, default), key)
        
        return config.get(key, default)
    
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