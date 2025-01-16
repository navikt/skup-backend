from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import apps, health, docs, devapps
from .database import engine
from .config import logger
from fastapi.openapi.utils import get_openapi
import os

app = FastAPI()

# Get SKIP_AUTH value
skip_auth = os.getenv("SKIP_AUTH", "false").lower() == "true"

# Configure CORS headers based on environment
allow_headers = ["Content-Type"]
if skip_auth:
    allow_headers.append("Authorization")
    logger.info("Development mode: Adding Authorization to CORS headers")

app.include_router(apps)
app.include_router(health)
app.include_router(docs)
app.include_router(devapps)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=allow_headers,
)

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        content={"message": "An internal server error occurred. Please try again later.", "details": str(exc)},
        status_code=500
    )

@app.on_event("startup")
async def startup():
    logger.info(f"SKIP_AUTH environment variable: {os.getenv('SKIP_AUTH')}")
    engine.connect()
    logger.info("Database connection established.")

@app.on_event("shutdown")
def shutdown():
    if engine.pool:
        engine.pool.dispose()
        logger.info("Database connection pool disposed.")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Your API Title",
        version="1.0.0",
        description="Your API description",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    # Ensure security is applied to all paths
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi