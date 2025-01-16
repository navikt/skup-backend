"""Innstillinger for prosjektet.

Denne filen inneholder både innstillinger vi setter for prosjektet, men også
innstillinger som vi må hente fra NAIS sine miljøvariabler.
"""

from pydantic import AliasChoices, AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Innstillinger for prosjektet"""

    """ Ved behov
    model_config = SettingsConfigDict(
        env_prefix="skup_fastapi_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )
    """

    client_id: str = Field(
        "skup-backend", validation_alias=AliasChoices("azure_app_client_id")
    )
    """Klient ID for applikasjonen"""

    well_known_url: AnyHttpUrl = Field(
        "http://localhost:8888/default/.well-known/openid-configuration",
        validation_alias=AliasChoices("azure_app_well_known_url"),
    )
    """URL som peker til Metadata Document Endpoint"""


# MERK: Vi ignorerer 'call-arg' for mypy ved instansiering på grunn av følgende
# bug: https://github.com/pydantic/pydantic/issues/6713
settings = Settings()  # type: ignore[call-arg]