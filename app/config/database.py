from app.config.logger import logger
from app.database import engine

def configure_database(app):
    @app.on_event("startup")
    async def startup():
        logger.info(f"SKIP_AUTH found - Development mode is enabled")
        engine.connect()
        logger.info("Database connection established.")

    @app.on_event("shutdown")
    def shutdown():
        if engine.pool:
            engine.pool.dispose()
            logger.info("Database connection pool released.")