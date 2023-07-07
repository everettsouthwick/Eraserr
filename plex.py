from plexapi.server import PlexServer
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("PLEX_BASE_URL")
TOKEN = os.getenv("PLEX_TOKEN")

plex = PlexServer(BASE_URL, TOKEN)


def get_sections(section_type):
    """
    Retrieves the section IDs for a given section type.

    Args:
        section_type (str): The type of section to retrieve.

    Returns:
        List[int]: A list of section IDs.
    """
    sections = []

    for section in plex.library.sections():
        if section.type == section_type:
            sections.append(section)

    return sections


def update_library(section):
    """
    Updates the given section.

    Args:
        section (plexapi.library.LibrarySection): The section to update.
    """
    section.update()


def find_and_update_library(section_type):
    """
    Finds and updates the given section type.

    Args:
        section_type (str): The type of section to update.
    """
    sections = get_sections(section_type)

    for section in sections:
        update_library(section)

    print(f"Updated {len(sections)} Plex {section_type} library.")
