"""Logger configuration for the application."""
import logging
import sys

from src.config import settings


def setup_logger() -> logging.Logger:
    """Initialize and configure the application logger."""
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("app.log")],
    )
    return logging.getLogger(__name__)


logger = setup_logger()
