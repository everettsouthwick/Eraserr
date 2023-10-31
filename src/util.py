"""This file contains utility functions for the project."""
from datetime import datetime
import pytz

def convert_bytes(num):
    """
    This function will convert bytes to MB, GB, or TB
    """
    for unit in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return f"{num:3.2f} {unit}".strip()
        num /= 1024.0

    return f"{num:3.2f}".strip()

def convert_seconds(num):
    """
    This function will convert seconds to minutes, hours, or days
    """
    for unit, duration in [("seconds", 60), ("minutes", 60), ("hours", 24)]:
        if num < duration:
            return f"{num:3.0f} {unit}".strip()
        num /= duration

    return f"{num:3.0f} days".strip()

def convert_to_datetime(iso_string):
    """
    This function will convert an ISO string to a datetime object
    """
    utc_dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    return utc_dt.astimezone(pytz.utc).replace(tzinfo=None)
