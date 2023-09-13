# Configuration
This guide contains all the information you need to configure `Eraserr` using a `config.json` file. An example file of the configuration can be found at [config.json.example](config.example.json).

## Table of Contents
- [General Settings](#general-settings)
  - [Dry Run](#dry-run)
  - [Log Level](#log-level)
  - [Schedule Interval](#schedule-interval)
- [Plex](#plex)
  - [Base URL](#plex-base-url)
  - [Token](#plex-token)
- [Radarr](#radarr)
  - [Enabled](#radarr-enabled)
  - [API Key](#radarr-api-key)
  - [Base URL](#radarr-base-url)
  - [Exempt Tag Names](#radarr-exempt-tag-names)
  - [Watched Deletion Threshold](#radarr-watched-deletion-threshold)
  - [Unwatched Deletion Threshold](#radarr-unwatched-deletion-threshold)
- [Sonarr](#sonarr)
  - [Enabled](#sonarr-enabled)
  - [API Key](#sonarr-api-key)
  - [Base URL](#sonarr-base-url)
  - [Monitor Continuing Series](#sonarr-monitor-continuing-series)
  - [Dynamic Load](#sonarr-dynamic-load)
  - [Exempt Tag Names](#sonarr-exempt-tag-names)
  - [Watched Deletion Threshold](#sonarr-watched-deletion-threshold)
  - [Unwatched Deletion Threshold](#sonarr-unwatched-deletion-threshold)
- [Overseerr](#overseerr)
  - [Enabled](#overseerr-enabled)
  - [API Key](#overseerr-api-key)
  - [Base URL](#overseerr-base-url)
  - [Fetch Limit](#overseerr-fetch-limit)

## General Settings

### Dry Run

```json
"dry_run": true
```

Set to `true` for a dry run. The program will log the actions it would take without making changes. Set to `false` to enable live mode where changes will be made. Update the `dry_run` value as per your requirements.

### Log Level

```json
"log_level": "INFO"
```

Set the log level for the application. Valid values are "INFO", "DEBUG", "WARN", "ERROR". Update the `log_level` value as per your requirements.

### Schedule Interval

```json
"schedule_interval": "1d"
```

Set the interval at which the script runs by replacing the `schedule_interval` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

## Plex

```json
"plex": {
    "base_url": "https://host:port",
    "token": ""
}
```

### Plex Base URL
Update the `base_url` with your Plex base URL.

### Plex Token
Replace the empty `token` value with your Plex token.

## Radarr

```json
"radarr": {
    "enabled": true,
    "api_key": "",
    "base_url": "https://host:port/api/v3",
    "exempt_tag_names": [
        "exempt-from-auto-delete",
        "some-other-tag"
    ],
    "watched_deletion_threshold": "180d",
    "unwatched_deletion_threshold": "30d"
}
```

### Radarr Enabled
Set to `true` to enable Radarr integration. Set to `false` to disable it.

### Radarr API Key
Replace the empty `api_key` value with your Radarr API Key.

### Radarr Base URL
Update the `base_url` with your Radarr base URL.

### Radarr Exempt Tag Names
Set tag names to exempt from automatic deletion by updating the `exempt_tag_names` array.

### Radarr Watched Deletion Threshold
Set the threshold for watched media deletion by replacing the `watched_deletion_threshold` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

### Radarr Unwatched Deletion Threshold
Set the threshold for unwatched media deletion by replacing the `unwatched_deletion_threshold` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

## Sonarr

```json
"sonarr": {
    "enabled": true,
    "api_key": "",
    "base_url": "https://host:port/api/v3",
    "monitor_continuing_series": true,
    "dynamic_load": {
        "enabled": false,
        "episodes_to_load": 3,
        "episodes_to_keep": 3,
        "watched_deletion_threshold": "30d",
        "schedule_interval": "5m"
    },
    "exempt_tag_names": [
        "exempt-from-auto-delete",
        "some-other-tag"
    ],
    "watched_deletion_threshold": "180d",
    "unwatched_deletion_threshold": "30d"
}
```

### Sonarr Enabled
Set to `true` to enable Sonarr integration. Set to `false` to disable it.

### Sonarr API Key
Replace the empty `api_key` value with your Sonarr API Key.

### Sonarr Base URL
Update the `base_url` with your Sonarr base URL.

### Sonarr Monitor Continuing Series
Set to `true` if you want to monitor continuing series instead of deleting it from Sonarr so that new seasons are fetched.

### Sonarr Dynamic Load
Configure the dynamic load settings as per your requirements. You can set the number of episodes to load, keep, the watched deletion threshold, and the schedule interval.

### Sonarr Exempt Tag Names
Set tag names to exempt from automatic deletion by updating the `exempt_tag_names` array.

### Sonarr Watched Deletion Threshold
Set the threshold for watched media deletion by replacing the `watched_deletion_threshold` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

### Sonarr Unwatched Deletion Threshold
Set the threshold for unwatched media deletion by replacing the `unwatched_deletion_threshold` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

## Overseerr

```json
"overseerr": {
    "enabled": true,
    "api_key": "",
    "base_url": "http://host:port/api/v1",
    "fetch_limit": 20
}
```

### Overseerr Enabled
Set to `true` to enable Overseerr integration. Set to `false` to disable it.

### Overseerr API Key
Replace the empty `api_key` value with your Overseerr API Key.

### Overseerr Base URL
Update the `base_url` with your Overseerr base URL.

### Overseerr Fetch Limit
Set the number of results to fetch from Overseerr by replacing the `fetch_limit` value.