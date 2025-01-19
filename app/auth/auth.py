import os
import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import AnyHttpUrl
from typing import Annotated, Any
from app.auth.settings import settings
from app.config.logger import logger

# Definerer OAuth2PasswordBearer for token-sikkerhet
token_security = OAuth2PasswordBearer(
    tokenUrl="token",
    auto_error=True
)

class VerifyOauth2Token:
    def __init__(self) -> None:
        # Sjekker om autentisering skal hoppes over
        self.skip_auth = os.getenv("SKIP_AUTH", "false").lower() == "true"
        logger.info(f"SKIP_AUTH er satt til: {self.skip_auth}")

        if not self.skip_auth:
            # Henter OIDC-konfigurasjon fra URL
            self.oidc_url: AnyHttpUrl = settings.well_known_url
            self.client_id: str = settings.client_id
            self.oidc_config: dict[str, Any] = (
                httpx.get(str(self.oidc_url)).raise_for_status().json()
            )
            # Initialiserer JWT-klient for å hente signeringsnøkler
            self.jwks_client: jwt.PyJWKClient = jwt.PyJWKClient(
                self.oidc_config["jwks_uri"]
            )
            # Henter signeringsalgoritmer og utsteder fra OIDC-konfigurasjon
            self.signing_algos: list[str] = self.oidc_config[
                "id_token_signing_alg_values_supported"
            ]
            self.issuer: str = self.oidc_config["issuer"]

    async def verify(
        self,
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(token_security)],
    ) -> dict[str, Any]:
        if self.skip_auth:
            # logger.info("Autentiseringskontroll omgått på grunn av SKIP_AUTH=true")
            return {"preferred_username": "local_user"}

        # Definerer en HTTPException for uautentisert tilgang
        unauthenticated_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ikke gyldig akkreditering",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Henter signeringsnøkkel fra JWT-token
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        except jwt.exceptions.PyJWKClientError:
            logger.exception(
                "Klarte ikke å hente signeringsnøkkel ",
                f"fra JWKS ({self.jwks_client.uri}) endepunkt!",
            )
            raise unauthenticated_exception
        except jwt.DecodeError:
            logger.exception("Klarte ikke å dekode token", token=token)
            raise unauthenticated_exception

        try:
            # Dekoder og verifiserer JWT-token
            payload: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=self.signing_algos,
                options={
                    "require": ["iss", "exp", "aud", "iat"],
                    "verify_signature": True,
                },
                audience=self.client_id,
                issuer=self.issuer,
                verify=True,
            )
        except jwt.InvalidTokenError:
            logger.exception("Kunne ikke validere akkreditering")
            raise unauthenticated_exception

        return payload