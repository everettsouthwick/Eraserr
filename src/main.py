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
    # Initialize the configuration
    config = Config()

    if args.dry_run:
        config.dry_run = args.dry_run
    if args.schedule_interval:
        config.schedule_interval = args.schedule_interval

    # Initialize and start job runner
    job_runner = JobRunner(config)
    job_runner.run()
