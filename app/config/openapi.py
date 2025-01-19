import os
from fastapi.openapi.utils import get_openapi

def configure_openapi(app):
    app_name = os.getenv("APP_NAME", "FastAPI")
    app_version = os.getenv("APP_VERSION", "1.0.0")
    app_description = os.getenv("APP_DESCRIPTION", "")

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app_name,
            version=app_version,
            description=app_description,
            routes=app.routes,
        )

        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "For local development: Use any token, e.g., `test-token`"
            }
        }

        for path, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                if "security" in operation:
                    operation["security"] = [{"bearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi