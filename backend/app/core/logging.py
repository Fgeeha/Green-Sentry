import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """Setup application logging"""

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # File handler
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(logging.Formatter(log_format))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Disable uvicorn access logs in production
    if not settings.DEBUG:
        logging.getLogger("uvicorn.access").disabled = True