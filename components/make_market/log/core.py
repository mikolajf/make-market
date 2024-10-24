import logging
import logging.handlers
from pathlib import Path


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a logger with the given name and level.

    Args:
        name (str): The name of the logger.
        level (int): The logging level (default is logging.INFO).

    Returns:
        logging.Logger: The configured logger.

    """
    logger = logging.getLogger(name)

    # setup formatter
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    formatter = logging.Formatter(fmt)

    # setup stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # file handler
    # TODO: get from settings
    log_dir = Path(__file__).parent.parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_dir / f"{name}.log", when="D", interval=1, backupCount=10
    )
    file_handler.setFormatter(formatter)

    # add handlers
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    logger.setLevel(level)

    return logger
