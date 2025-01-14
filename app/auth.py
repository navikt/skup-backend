#!/usr/bin/env python3

"""Autentiseringstøtte for FastAPI."""

from typing import Annotated, Any

import httpx
import jwt
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import OpenIdConnect, SecurityScopes
from pydantic import AnyHttpUrl

from nais_fastapi_template.settings import settings

token_security = OpenIdConnect(openIdConnectUrl=str(settings.well_known_url))
"""Definisjon av hvordan token autentisering må håndteres"""

log = structlog.get_logger("api.auth")
"""Log for feilmeldinger"""


class VerifyOauth2Token:
    """Klasse som støtter verifisering av NAIS OAuth2 token i FastAPI."""

    def __init__(self) -> None:
        """Opprett en ny instans ved å sjekke metadata discovery document."""
        self.oidc_url: AnyHttpUrl = settings.well_known_url
        self.client_id: str = settings.client_id
        # Hent OIDC konfigurasjon fra angitt URL
        self.oidc_config: dict[str, Any] = (
            httpx.get(str(self.oidc_url)).raise_for_status().json()
        )
        self.jwks_client: jwt.PyJWKClient = jwt.PyJWKClient(
            self.oidc_config["jwks_uri"]
        )
        self.signing_algos: list[str] = self.oidc_config[
            "id_token_signing_alg_values_supported"
        ]
        self.issuer: str = self.oidc_config["issuer"]

    async def verify(
        self,
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(token_security)],
    ) -> dict[str, Any]:
        """Verifiser at spørring har gyldig Entra ID token."""
        unauthenticated_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ikke gyldig akkreditering",
            headers={"WWW-Authenticate": "Bearer"},
        )
        scheme, token = token.split(" ", maxsplit=1)
        if scheme != "Bearer":
            log.error("Ukjent autentisering scheme", token=token, scheme=scheme)
            raise unauthenticated_exception
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        except jwt.exceptions.PyJWKClientError:
            log.exception(
                "Klarte ikke å hente signeringsnøkkel ",
                f"fra JWKS ({self.jwks_client.uri}) endepunkt!",
            )
            raise unauthenticated_exception
        except jwt.DecodeError:
            log.exception("Klarte ikke å dekode token", token=token)
            raise unauthenticated_exception

        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=self.signing_algos,
                # Basert på NAIS sin dokumentasjon, skal en token inneholde:
                # https://doc.nais.io/auth/explanations/#claims-validation
                options={
                    "require": ["iss", "exp", "aud", "iat"],
                    "verify_signature": True,
                },
                audience=self.client_id,
                issuer=self.issuer,
                verify=True,
            )
        except jwt.InvalidTokenError:
            log.exception("Kunne ikke validere akkreditering")
            raise unauthenticated_exception
        granted_scopes = payload.get("scp", "").split(" ")
        for needed_scope in security_scopes.scopes:
            if needed_scope not in granted_scopes:
                log.warning(
                    "Bruker mangler adganger",
                    needed_scopes=security_scopes.scopes,
                    granted_scopes=granted_scopes,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bruker mangler adganger",
                )
        return payload