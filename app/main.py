from fastapi import FastAPI
from app.routers import include_routers
from app.config import configure_cors, configure_database, configure_exceptions, configure_openapi

app = FastAPI()

# Router
include_routers(app)

# Konfig
configure_cors(app)
configure_database(app)
configure_exceptions(app)
configure_openapi(app)