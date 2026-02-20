import logging
from app.config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    """Get configured logger"""
    return logging.getLogger(name)
