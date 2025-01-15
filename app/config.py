"""Global configuration for the application."""

from dotenv import load_dotenv
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseSettingsConfig(BaseSettings):
    """Base configuration for all settings classes"""

    model_config = SettingsConfigDict(
        env_prefix="nais_fastapi_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )