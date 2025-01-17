# Innstillinger for autentisering.
# Denne filen inneholder innstillinger som vi må hente fra NAIS sine miljøvariabler.

from pydantic import AliasChoices, AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Klient ID for applikasjonen
    client_id: str = Field(
        "skup-backend", validation_alias=AliasChoices("azure_app_client_id")
    )

    # URL som peker til Metadata Document Endpoint
    well_known_url: AnyHttpUrl = Field(
        "http://localhost:8888/default/.well-known/openid-configuration",
        validation_alias=AliasChoices("azure_app_well_known_url"),
    )

# MERK: Vi ignorerer 'call-arg' for mypy ved instansiering på grunn av følgende
# bug: https://github.com/pydantic/pydantic/issues/6713
settings = Settings()  # type: ignore[call-arg]