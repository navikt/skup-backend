from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)