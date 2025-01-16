from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .database import engine
from .config import logger
from fastapi.openapi.utils import get_openapi
import os
from app.routers import apps, health, docs

app = FastAPI()

# Inkluder alle API-rutere
app.include_router(apps)
app.include_router(health)
app.include_router(docs)

# SKIP_AUTH verdi avgjør om NAIS Auth skla kjøres eller ikke
skip_auth = os.getenv("SKIP_AUTH", "false").lower() == "true"

# Konfigurer CORS-headers basert på miljø
allow_headers = ["Content-Type"]
if skip_auth:
    allow_headers.append("Authorization")
    logger.info("Utviklingsmodus: Legger til Authorization i CORS-headers")

# Konfigurer CORS-middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=allow_headers,
)

# Håndter alle uventede feil
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Uhåndtert feil: {exc}")
    return JSONResponse(
        content={"message": "En intern serverfeil oppstod. Vennligst prøv igjen senere.", "details": str(exc)},
        status_code=500
    )

# Oppstartshendelse
@app.on_event("startup")
async def startup():
    logger.info(f"SKIP_AUTH funnet - Utviklingsmodus er aktivert")
    engine.connect()
    logger.info("Databasetilkobling etablert.")

# Avslutningshendelse
@app.on_event("shutdown")
def shutdown():
    if engine.pool:
        engine.pool.dispose()
        logger.info("Databasetilkoblingspool frigjort.")

# Tilpass OpenAPI-dokumentasjon med sikkerhetskrav
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Skup API",
        version="1.0.0",
        description="",
        routes=app.routes,
    )
    
    # Legg til sikkerhetsskjema for JWT
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Legg til en tilfeldig token. Eksempelvis: `test-token`"
        }
    }
    
    # Legg til globalt sikkerhetskrav
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    # Sikre at sikkerhet er påkrevd for alle endepunkter
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi