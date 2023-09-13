"""eraserr.py: A script to remove expired media from Plex, Radarr, Sonarr, and Overseerr."""
import argparse
from src.main import main

__version__ = "2.0.0"

def add_arguments(arg_parser: argparse.ArgumentParser):
    '''
    Adds arguments to the given ArgumentParser object.
    
    Args:
        arg_parser (argparse.ArgumentParser): The ArgumentParser object to add arguments to.

    Returns:
      None
    '''
    arg_parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}", help="show the current version and exit"
    )

    arg_parser.add_argument("-d", "--dry-run", action="store_true", help="perform a trial run without any changes made")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse command line arguments")
    add_arguments(parser)
    args = parser.parse_args()

    try:
        main(args)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping all checks")
