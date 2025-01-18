from .apps import router as apps
from .health import router as health
from .docs import router as docs

# Inkluder API-rutere
def include_routers(app):
    app.include_router(apps)
    app.include_router(health)
    app.include_router(docs)