# app/config/cors.py
import os
from fastapi.middleware.cors import CORSMiddleware
from app.config.logger import logger

def configure_cors(app):
    skip_auth = os.getenv("SKIP_AUTH", "false").lower() == "true"
    allow_headers = ["Content-Type"]
    if skip_auth:
        allow_headers.append("Authorization")
        logger.info("Development mode: Adding Authorization to CORS headers")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE", "PUT"],
        allow_headers=allow_headers,
    )