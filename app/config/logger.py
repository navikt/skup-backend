import os
import logging

logging_level = os.getenv("LOGGING_LEVEL", "WARNING")

# Konfigurer logging
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)