# app/auth/auth.py

import os
import httpx
import jwt
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import AnyHttpUrl
from typing import Annotated, Any

from app.auth.settings import settings

token_security = OAuth2PasswordBearer(
    tokenUrl="token",
    auto_error=True
)
log = structlog.get_logger("api.auth")

class VerifyOauth2Token:
    def __init__(self) -> None:
        self.skip_auth = os.getenv("SKIP_AUTH", "false").lower() == "true"
        log.info(f"Auth initialization - SKIP_AUTH is set to: {self.skip_auth}")
        if not self.skip_auth:
            self.oidc_url: AnyHttpUrl = settings.well_known_url
            self.client_id: str = settings.client_id
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
        log.info(f"Verifying token with SKIP_AUTH={self.skip_auth}")
        if self.skip_auth:
            log.info("Auth check bypassed due to SKIP_AUTH=true")
            return {"preferred_username": "local_user"}

        unauthenticated_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ikke gyldig akkreditering",
            headers={"WWW-Authenticate": "Bearer"},
        )
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

        return payload