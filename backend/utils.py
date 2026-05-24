import os
import sys
import logging
from typing import Optional

# Setup standard logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("GitHub_Automation")

def ensure_directory(path: str) -> None:
    """Creates a directory if it doesn't exist."""
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Directory verified: {path}")
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        sys.exit(1)

def get_env_var(name: str, default: Optional[str] = None) -> str:
    """Safely retrieves environment variables."""
    value = os.environ.get(name, default)
    if not value:
        logger.error(f"Critical environment variable missing: {name}")
        sys.exit(1)
    return value
