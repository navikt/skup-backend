from dotenv import load_dotenv
import logging

# Last miljøvariabler
load_dotenv()

# Konfigurer logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)