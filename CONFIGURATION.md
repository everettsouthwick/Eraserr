# Configuration
This guide contains all the information you need to configure `Eraserr` using an `.env` file. An example file of the configuration can be found at [.env.example](.env.example).

## Table of Contents
- [Tautulli](#tautulli)
  - [API Key](#tautulli-api-key)
  - [Base URL](#tautulli-base-url)
  - [Fetch Limit](#tautulli-fetch-limit)
- [Radarr](#radarr)
  - [API Key](#radarr-api-key)
  - [Base URL](#radarr-base-url)
- [Sonarr](#sonarr)
  - [API Key](#sonarr-api-key)
  - [Base URL](#sonarr-base-url)
- [Overseerr](#overseerr)
  - [API Key](#overseerr-api-key)
  - [Base URL](#overseerr-base-url)
  - [Fetch Limit](#overseerr-fetch-limit)
- [Days Threshold](#days-threshold)
- [Dry Run](#dry-run)
- [Schedule Interval](#schedule-interval)

## Tautulli

### Tautulli API Key
`TAUTULLI_API_KEY=your_api_key_here`

Enter your Tautulli API Key here.

### Tautulli Base URL
`TAUTULLI_BASE_URL=http://host:port/api/v2`

Enter your Tautulli base URL here.

### Tautulli Fetch Limit
`TAUTULLI_FETCH_LIMIT=25`

Set the number of results to fetch from Tautulli.

## Radarr

### Radarr API Key
`RADARR_API_KEY=your_api_key_here`

Enter your Radarr API Key here.

### Radarr Base URL
`RADARR_BASE_URL=http://host:port/api/v3`

Enter your Radarr base URL here.

## Sonarr

### Sonarr API Key
`SONARR_API_KEY=your_api_key_here`

Enter your Sonarr API Key here.

### Sonarr Base URL
`SONARR_BASE_URL=http://host:port/api/v3`

Enter your Sonarr base URL here.

## Overseerr

### Overseerr API Key
`OVERSEERR_API_KEY=your_api_key_here`

Enter your Overseerr API Key here.

### Overseerr Base URL
`OVERSEERR_BASE_URL=http://host:port/api/v1`

Enter your Overseerr base URL here.

### Overseerr Fetch Limit
`OVERSEERR_FETCH_LIMIT=10`

Set the number of results to fetch from Overseerr.

## Days Threshold
`DAYS_THRESHOLD=30`

Set the days threshold for media deletion. Any media not watched in the past given number of days will be considered stale and flagged for deletion.

## Dry Run
`DRY_RUN=True`

Set to `True` for dry run. The program will log the actions it would take without making changes. Set to `False` to enable live mode where changes will be made.

## Schedule Interval
`SCHEDULE_INTERVAL=86400`

Set the interval (in seconds) at which the script runs.
