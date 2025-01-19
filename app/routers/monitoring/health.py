from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal

router = APIRouter()

# Sjekker om applikasjonen er i live
@router.get("/api/isalive", tags=["Health"])
def read_isalive():
    return {"message": "Alive"}

# Sjekker om applikasjonen er klar
@router.get("/api/isready", tags=["Health"])
def read_isready():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"message": "Ready"}
    except SQLAlchemyError:
        return {"message": "Database connection failed"}, 503