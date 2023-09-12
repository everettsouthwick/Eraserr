"""This module is used to configure the logger for the application."""
import logging
from src.config import Config

config = Config()

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(config.log_level))

file_handler = logging.FileHandler('app.log')
stream_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
