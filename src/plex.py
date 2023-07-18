from plexapi.server import PlexServer
import time


class PlexClient:
    def __init__(self, config):
        self.config = config
        self.base_url = config.plex.base_url
        self.token = config.plex.token
        self.refresh = config.plex.refresh
        self.plex = PlexServer(self.base_url, self.token)

    def get_sections(self, section_type):
        """
        Retrieves the section IDs for a given section type.

        Args:
            section_type (str): The type of section to retrieve.

        Returns:
            List[int]: A list of section IDs.
        """
        sections = []

        for section in self.plex.library.sections():
            if section.type == section_type:
                sections.append(section)

        return sections

    def update_library(self, section):
        """
        Updates the given section.

        Args:
            section (plexapi.library.LibrarySection): The section to update.
        """
        section.update()

    def find_and_update_library(self, section_type):
        """
        Finds and updates the given section type.

        Args:
            section_type (str): The type of section to update.
        """
        sections = self.get_sections(section_type)

        for section in sections:
            self.update_library(section)
            refreshing = self.plex.library.sectionByID(section.key).refreshing
            sleep_time = 5
            max_refresh_time = 300

            while refreshing and max_refresh_time > 0:
                refreshing = self.plex.library.sectionByID(section.key).refreshing
                print(f"PLEX :: Waiting for {section.title} to finish updating...")
                max_refresh_time -= sleep_time
                time.sleep(sleep_time)

        print(f"PLEX :: Updated {len(sections)} Plex {section_type} library")
