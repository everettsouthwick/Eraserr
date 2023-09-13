"""This file contains utility functions for the project."""
def convert_bytes(num):
    """
    This function will convert bytes to MB, GB, or TB
    """
    for unit in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return f"{num:3.2f} {unit}"
        num /= 1024.0

    return f"{num:3.2f}"
