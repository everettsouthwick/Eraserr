"""Main module for the application."""
from src.config import Config
from src.jobs import JobRunner


def main(args):
    """
    Initializes the configuration and starts the job runner.

    Args:
        args: Command line arguments.

    Returns:
        None
    """
    config = Config()

    if args.dry_run:
        config.dry_run = args.dry_run

    job_runner = JobRunner(config)
    job_runner.run()
