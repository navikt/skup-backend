from app.routers.apps import router as apps
from app.routers.monitoring import health, docs

# Inkluder API-rutere
def include_routers(app):
    app.include_router(apps)
    app.include_router(health)
    app.include_router(docs)