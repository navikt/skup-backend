"""Innstillinger for autentisering.

Denne filen inneholder innstillinger relatert til autentisering og Azure AD.
"""

from pydantic import AliasChoices, AnyHttpUrl, Field

class Settings(BaseSettingsConfig):
    """Innstillinger for autentisering"""

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