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
    - [Enabled](#enabled)
    - [Episodes to Load](#episodes-to-load)
    - [Episodes to Keep](#episodes-to-keep)
    - [Watched Deletion Threshold](#watched-deletion-threshold)
    - [Schedule Interval](#schedule-interval)
    - [Additional Information](#additional-information)
  - [Exempt Tag Names](#sonarr-exempt-tag-names)
  - [Watched Deletion Threshold](#sonarr-watched-deletion-threshold)
  - [Unwatched Deletion Threshold](#sonarr-unwatched-deletion-threshold)
- [Overseerr](#overseerr)
  - [Enabled](#overseerr-enabled)
  - [API Key](#overseerr-api-key)
  - [Base URL](#overseerr-base-url)
  - [Fetch Limit](#overseerr-fetch-limit)
- [Experimental](#experimental)
  - [Free Space Configuration](#free-space-configuration)
    - [Enabled](#free-space-enabled)
    - [Minimum Free Space Percentage](#minimum-free-space-percentage)
    - [Path](#path)

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

Configure the dynamic load settings to efficiently manage your media storage on the Plex server. This feature preloads episodes ahead of the current viewing point and deletes watched episodes, saving substantial storage space. It considers the viewing patterns of multiple users to prevent premature deletion of episodes being watched concurrently.

Here is an example of `episodes_to_load` = 3 and `episodes_to_keep` = 2 and you are viewing the first season. The first number of `episodes_to_keep` of a series (Season 1) will _always_ be kept. This means that deletion will only kick in when you reach E6 because E1 and E2 are protected, and E4 and E5 are the 2 episodes prior to E6, so only E3 is eligible for deletion in that scenario.

![image](https://github.com/everettsouthwick/Eraserr/assets/8216991/2e6f972c-de55-48a6-afb0-be1a49499f66)

#### Enabled
Toggle this setting to activate or deactivate the dynamic load feature.

#### Episodes to Load
Specify the number of future episodes to preload. When a user starts watching a TV show, it will download the specified number of episodes ahead of where they are currently watching.

#### Episodes to Keep
Specify the minimum number of episodes to retain. When a user starts watching a TV show, it will delete the specified number of episodes behind of where they are currently watching.

#### Watched Deletion Threshold
Set the timeframe to consider multiple users' viewing patterns before deleting any episodes, preventing the removal of episodes being watched by different users within the specified period. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

#### Schedule Interval
Set the interval at which dynamic load runs by replacing the `schedule_interval` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

#### Additional Information
Utilize the exempt tags to exclude specific series from dynamic loading, ensuring they remain available for repeated viewing.

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

## Experimental

The experimental section contains configurations that are in the testing phase. These settings may be subject to changes and updates. Use them at your own risk.

### Free Space Configuration

```json
"experimental": {
    "free_space": {
        "enabled": false,
        "minimum_free_space_percentage": 20,
        "path": "/mnt/local/Media"
    }
}
```

#### Enabled

```json
"enabled": false
```

Toggle this setting to enable or disable the free space feature. When enabled, the program will monitor the specified path to ensure that the minimum free space threshold is maintained.

#### Minimum Free Space

```json
"minimum_free_space_percentage": 20
```

Define the minimum free space as a percentage of the total space that should be maintained in the specified path. The program will attempt to free up space if the available space falls below this threshold. The value should be between 0 and 100, representing the percentage of free space to maintain.

#### Path

```json
"path": "/mnt/local/Media"
```

Specify the path that should be monitored for free space. Ensure to update this with the correct path where your media files are stored.

**Note**: This feature is experimental and might not work as expected in all scenarios. It is recommended to use it with caution and monitor its behavior closely to prevent any unintended data loss.