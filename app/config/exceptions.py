from fastapi.responses import JSONResponse
from app.config.logger import logger

def configure_exceptions(app):
    @app.exception_handler(Exception)
    async def generic_exception_handler(request, exc):
        logger.error(f"Unhandled error: {exc}")
        return JSONResponse(
            content={"message": "An internal server error occurred. Please try again later.", "details": str(exc)},
            status_code=500
        )