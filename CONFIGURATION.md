# Configuration
This guide contains all the information you need to configure `Eraserr` using a `config.json` file. An example file of the configuration can be found at [config.json.example](config.example.json).

## Table of Contents
- [General Settings](#general-settings)
  - [Dry Run](#dry-run)
  - [Log Level](#log-level)
  - [Schedule Interval](#schedule-interval)
- [Plex](#plex)
  - [Base URL](#base-url)
  - [Token](#token)
- [Radarr](#radarr)
  - [Enabled](#enabled)
  - [API Key](#api-key)
  - [Base URL](#base-url-1)
  - [Exempt Tag Names](#exempt-tag-names)
  - [Watched Deletion Threshold](#watched-deletion-threshold)
  - [Unwatched Deletion Threshold](#unwatched-deletion-threshold)
- [Sonarr](#sonarr)
  - [Enabled](#enabled-1)
  - [API Key](#api-key-1)
  - [Base URL](#base-url-2)
  - [Monitor Continuing Series](#monitor-continuing-series)
  - [Dynamic Load](#dynamic-load)
    - [Enabled](#enabled-2)
    - [Episodes to Load](#episodes-to-load)
    - [Episodes to Keep](#episodes-to-keep)
    - [Watched Deletion Threshold](#watched-deletion-threshold-1)
    - [Schedule Interval](#schedule-interval)
  - [Exempt Tag Names](#exempt-tag-names-1)
  - [Watched Deletion Threshold](#watched-deletion-threshold-2)
  - [Unwatched Deletion Threshold](#unwatched-deletion-threshold-1)
- [Overseerr](#overseerr)
  - [Enabled](#enabled-3)
  - [API Key](#api-key-2)
  - [Base URL](#base-url-3)
  - [Fetch Limit](#fetch-limit)
- [Experimental](#experimental)
  - [Free Space](#free-space)
    - [Enabled](#enabled-4)
    - [Minimum Free Space Percentage](#minimum-free-space-percentage)
    - [Path](#path)
    - [Prevent Age-Based Deletion](#prevent-age-based-deletion)
    - [Prevent Dynamic Load](#prevent-dynamic-load)
    - [Progressive Deletion](#progressive-deletion)
      - [Enabled](#enabled-5)
      - [Maximum Deletion Cycles](#maximum-deletion-cycles)
      - [Threshold Reduction Per Cycle](#threshold-reduction-per-cycle)

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
    "base_url": "https://plex.domain.com",
    "token": ""
}
```

### Base URL
Update the `base_url` with your Plex base URL.

### Token
Replace the empty `token` value with your Plex token.

## Radarr

```json
"radarr": {
    "enabled": true,
    "api_key": "",
    "base_url": "https://radarr.domain.com/api/v3",
    "exempt_tag_names": [
        "exempt-from-auto-delete",
        "some-other-tag"
    ],
    "watched_deletion_threshold": "180d",
    "unwatched_deletion_threshold": "30d"
}
```

### Enabled
Set to `true` to enable Radarr integration. Set to `false` to disable it.

### API Key
Replace the empty `api_key` value with your Radarr API Key.

### Base URL
Update the `base_url` with your Radarr base URL.

### Exempt Tag Names
Set tag names to exempt from automatic deletion by updating the `exempt_tag_names` array.

### Watched Deletion Threshold
Set the threshold for watched media deletion by replacing the `watched_deletion_threshold` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

### Unwatched Deletion Threshold
Set the threshold for unwatched media deletion by replacing the `unwatched_deletion_threshold` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

## Sonarr

```json
"sonarr": {
    "enabled": true,
    "api_key": "",
    "base_url": "https://sonarr.domain.com/api/v3",
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

### Enabled
Set to `true` to enable Sonarr integration. Set to `false` to disable it.

### API Key
Replace the empty `api_key` value with your Sonarr API Key.

### Base URL
Update the `base_url` with your Sonarr base URL.

### Monitor Continuing Series
Set to `true` if you want to monitor continuing series instead of deleting it from Sonarr so that new seasons are fetched.

### Dynamic Load

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

### Exempt Tag Names
Set tag names to exempt from automatic deletion by updating the `exempt_tag_names` array.

### Watched Deletion Threshold
Set the threshold for watched media deletion by replacing the `watched_deletion_threshold` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

### Unwatched Deletion Threshold
Set the threshold for unwatched media deletion by replacing the `unwatched_deletion_threshold` value. The value should be in the format `<integer><d/h/m/s>` (days, hours, minutes, seconds).

## Overseerr

```json
"overseerr": {
    "enabled": true,
    "api_key": "",
    "base_url": "https://overseerr.domain.com/api/v1",
    "fetch_limit": 20
}
```

### Enabled
Set to `true` to enable Overseerr integration. Set to `false` to disable it.

### API Key
Replace the empty `api_key` value with your Overseerr API Key.

### Base URL
Update the `base_url` with your Overseerr base URL.

### Fetch Limit
Set the number of results to fetch from Overseerr by replacing the `fetch_limit` value.

## Experimental

The experimental section contains configurations that are in the testing phase. These settings may be subject to changes and updates. Use them at your own risk.

### Free Space

```json
"experimental": {
    "free_space": {
        "enabled": false,
        "minimum_free_space_percentage": 20,
        "path": "/mnt/local/Media",
        "prevent_age_based_deletion": true,
        "prevent_dynamic_load": true,
        "progressive_deletion": {
            "enabled": false,
            "maximum_deletion_cycles": 0,
            "threshold_reduction_per_cycle": "1d"
        }
    }
}
```

#### Enabled

```json
"enabled": false
```

Toggle this setting to enable or disable the free space feature. When enabled, the program will monitor the specified path to ensure that the minimum free space threshold is maintained.

**Note**: This feature is experimental and might not work as expected in all scenarios. It is recommended to use it with caution and monitor its behavior closely to prevent any unintended data loss.

#### Minimum Free Space Percentage

```json
"minimum_free_space_percentage": 20
```

Define the minimum free space as a percentage of the total space that should be maintained in the specified path. The program will attempt to free up space if the available space falls below this threshold. The value should be between 0 and 100, representing the percentage of free space to maintain.

#### Path

```json
"path": "/mnt/local/Media"
```

Specify the path that should be monitored for free space. Ensure to update this with the correct path where your media files are stored.

#### Prevent Age-Based Deletion

```json
"prevent_age_based_deletion": true
```

When enabled, this setting prevents the deletion of files based on their age, overriding the traditional age-based deletion mechanism. This is to ensure that the free space feature does not delete files that have surpassed a certain age threshold, helping to maintain the minimum free space requirement without compromising older files.

#### Prevent Dynamic Load

```json
"prevent_dynamic_load": true
```

This setting, when enabled, prevents the dynamic load feature from functioning if the free space is above the minimum threshold. This is to avoid unnecessary loading and deletion of files, ensuring that the system maintains a healthy free space level without overloading the storage with new files.

#### Progressive Deletion

Progressive deletion initiates a systematic process that lowers the deletion thresholds in each cycle, either until the free space exceeds the minimum threshold or until the maximum number of cycles (defined by `maximum_deletion_cycles`) is reached. 

##### Enabled

```json
"enabled": true
```

By setting this to true, you activate the progressive deletion process. This methodical approach to file deletion helps maintain the minimum free space threshold by recursively deleting files, reducing the deletion thresholds step by step in each cycle. It's a potent feature that can potentially remove a significant number of files in a short period, so it should be used with caution. Users are advised to monitor its behavior closely to prevent unintended data loss.

**Note**: This feature is powerful and can potentially delete a large number of files in a short period. It is recommended to use this feature judiciously and to monitor its behavior closely to prevent unintended data loss.

##### Maximum Deletion Cycles

```json
"maximum_deletion_cycles": 14
```

This parameter sets a limit on the number of recursive deletion cycles the system can execute during a progressive deletion operation. It serves as a protective measure to prevent excessive deletions, halting the operation after the specified number of cycles, even if the minimum free space threshold hasn't been achieved. The value should be an integer representing the maximum number of deletion cycles permitted.

##### Threshold Reduction Per Cycle

```json
"threshold_reduction_per_cycle": "1d"
```

This parameter specifies the amount by which the deletion threshold is reduced in each cycle. By lowering the deletion thresholds by the specified time interval (in this case, 1 day) during each cycle, the system can progressively free up more space. The value should be formatted as `<integer><d/h/m/s>` (days, hours, minutes, seconds), representing the time interval for threshold reduction.
