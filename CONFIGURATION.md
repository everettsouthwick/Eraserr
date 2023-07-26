# Configuration
This guide contains all the information you need to configure `Eraserr` using a `config.json` file. An example file of the configuration can be found at [config.json.example](config.example.json).

## Table of Contents
- [Tautulli](#tautulli)
  - [API Key](#tautulli-api-key)
  - [Base URL](#tautulli-base-url)
  - [Fetch Limit](#tautulli-fetch-limit)
- [Radarr](#radarr)
  - [API Key](#radarr-api-key)
  - [Base URL](#radarr-base-url)
  - [Exempt Tag Names](#radarr-exempt-tag-names)
- [Sonarr](#sonarr)
  - [API Key](#sonarr-api-key)
  - [Base URL](#sonarr-base-url)
  - [Monitor Continuing Series](#sonarr-monitor-continuing-series)
  - [Exempt Tag Names](#sonarr-exempt-tag-names)
- [Overseerr](#overseerr)
  - [API Key](#overseerr-api-key)
  - [Base URL](#overseerr-base-url)
  - [Fetch Limit](#overseerr-fetch-limit)
- [Plex](#plex)
  - [Base URL](#plex-base-url)
  - [Token](#plex-token)
- [Last Watched Days Deletion Threshold](#last-watched-days-deletion-threshold)
- [Unwatched Days Deletion Threshold](#unwatched-days-deletion-threshold)
- [Dry Run](#dry-run)
- [Schedule Interval](#schedule-interval)

## Tautulli

```json
"tautulli": {
    "api_key": "",
    "base_url": "http://host:port/api/v2",
    "fetch_limit": 25
}
```

### Tautulli API Key
Replace the empty `api_key` value with your Tautulli API Key.

### Tautulli Base URL
Update the `base_url` with your Tautulli base URL.

### Tautulli Fetch Limit
Set the number of results to fetch from Tautulli by replacing the `fetch_limit` value.

## Radarr

```json
"radarr": {
    "api_key": "",
    "base_url": "http://host:port/api/v3",
    "exempt_tag_names": [
        "exempt-from-auto-delete",
        "some-other-tag"
    ]
}
```

### Radarr API Key
Replace the empty `api_key` value with your Radarr API Key.

### Radarr Base URL
Update the `base_url` with your Radarr base URL.

### Radarr Exempt Tag Names
Set tag names to exempt from automatic deletion by updating the `exempt_tag_names` array.

## Sonarr

```json
"sonarr": {
    "api_key": "",
    "base_url": "http://host:port/api/v3",
    "monitor_continuing_series": true,
    "exempt_tag_names": [
        "exempt-from-auto-delete",
        "some-other-tag"
    ]
}
```

### Sonarr API Key
Replace the empty `api_key` value with your Sonarr API Key.

### Sonarr Base URL
Update the `base_url` with your Sonarr base URL.

### Sonarr Monitor Continuing Series
Set to `true` if you want to monitor continuing series instead of deleting it from Sonarr so that new seasons are fetched.

### Sonarr Exempt Tag Names
Set tag names to exempt from automatic deletion by updating the `exempt_tag_names` array.

## Overseerr

```json
"overseerr": {
    "api_key": "",
    "base_url": "http://host:port/api/v1",
    "fetch_limit": 10
}
```

### Overseerr API Key
Replace the empty `api_key` value with your Overseerr API Key.

### Overseerr Base URL
Update the `base_url` with your Overseerr base URL.

### Overseerr Fetch Limit
Set the number of results to fetch from Overseerr by replacing the `fetch_limit` value.

## Plex

```json
"plex": {
    "base_url": "http://host.port",
    "token": "",
    "refresh": true
}
```

### Plex Base URL
Update the `base_url` with your Plex base URL.

### Plex Token
Replace the empty `token` value with your Plex token.

### Plex Refresh
Set to `true` to refresh your Plex library. The program will refresh your Plex library after completion. Set to `false` to disable refreshing your Plex library. Update the `refresh` value as per your requirements.

## Days Threshold

```json
"days_threshold": 30
```

Set the days threshold for media deletion. Any media not watched in the past given number of days will be considered stale and flagged for deletion. Replace `days_threshold` with the desired value.

## Dry Run

```json
"dry_run": true
```

Set to `true` for dry run. The program will log the actions it would take without making changes. Set to `false` to enable live mode where changes will be made. Update the `dry_run` value as per your requirements.

## Schedule Interval

```json
"schedule_interval": 86400
```

Set the interval (in seconds) at which the script runs by replacing the `schedule_interval` value.
