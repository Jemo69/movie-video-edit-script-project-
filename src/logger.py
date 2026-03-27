import logging
import sys
from pathlib import Path

def get_logger(name):
    """
    Create and configure a logger with console and file handlers.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if handlers haven't been added yet
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Create log directory if it doesn't exist
    log_dir = Path('log')
    log_dir.mkdir(exist_ok=True)

    # Create handlers
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)  # Console shows INFO and above

    file_handler = logging.FileHandler(log_dir / 'app.log')
    file_handler.setLevel(logging.DEBUG)  # File captures everything

    # Create formatters and add to handlers
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    stdout_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    return logger