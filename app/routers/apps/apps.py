from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Security
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import UUID4
from app.config.logger import logger
from app.database import get_db
from app.routers.apps.models import Apps
from app.routers.apps.schemas import AppsModel, AppsResponseModel, AppsUpdateModel
from app.auth import VerifyOauth2Token

router = APIRouter()

# Initialiser token-verifisering
token_verification = VerifyOauth2Token()

# Opprett ny app
@router.post("/api/apps", response_model=AppsModel, tags=["Apps"])
async def add_app(
    apps: AppsModel,
    db: Session = Depends(get_db),
    token: Dict[str, Any] = Security(token_verification.verify)
):
    if not apps.app_name:
        raise HTTPException(status_code=400, detail="Du må oppgi et appnavn.")

    app_owner = token.get("preferred_username")
    if not app_owner:
        raise HTTPException(status_code=400, detail="Token inneholder ikke preferred_username.")

    # Sjekk om appnavn er unikt
    existing_app = db.query(Apps).filter(Apps.app_name == apps.app_name).first()
    if existing_app:
        raise HTTPException(status_code=400, detail="En app med dette navnet eksisterer allerede. Du må velge et unikt appnavn.")

    new_app = Apps(
        app_name=apps.app_name,
        app_owner=app_owner,
        created_at=datetime.utcnow().replace(microsecond=0)
    )
    try:
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        return new_app
    except Exception as e:
        db.rollback()
        logger.error(f"Kunne ikke legge til app: {e}")
        raise HTTPException(status_code=500, detail="Kunne ikke legge til app.")

# Hent alle apper eller filtrer etter app_id, app_name eller app_owner (delvis samsvar)
@router.get("/api/apps", response_model=List[AppsResponseModel], tags=["Apps"])
async def get_apps(
    app_id: Optional[UUID4] = Query(None),
    app_name: Optional[str] = Query(None),
    app_owner: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    token: Dict[str, Any] = Security(token_verification.verify)
):
    try:
        query = db.query(Apps)
        if app_id:
            query = query.filter(Apps.app_id == app_id)
        if app_name:
            query = query.filter(Apps.app_name.like(f"%{app_name}%"))
        if app_owner:
            query = query.filter(Apps.app_owner.like(f"%{app_owner}%"))
        results = query.all()
        if not results:
            return []
        return [AppsResponseModel.from_orm(result) for result in results]
    except Exception as e:
        logger.error(f"Kunne ikke hente apper: {e}")
        raise HTTPException(status_code=500, detail="Kunne ikke hente apper.")

# Slett en app etter app_id
@router.delete("/api/apps/{app_id}", response_model=AppsResponseModel, tags=["Apps"])
async def delete_app(
    app_id: UUID4,
    db: Session = Depends(get_db),
    token: Dict[str, Any] = Security(token_verification.verify)
):
    try:
        app_to_delete = db.query(Apps).filter(Apps.app_id == app_id).first()
        if not app_to_delete:
            raise HTTPException(status_code=404, detail="App ikke funnet")

        db.delete(app_to_delete)
        db.commit()
        return app_to_delete
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Kunne ikke slette app: {e}")
        raise HTTPException(status_code=500, detail="Kunne ikke slette app.")

# Oppdater app-detaljer
@router.put("/api/apps/{app_id}", response_model=AppsResponseModel, tags=["Apps"])
async def update_app(
    app_id: UUID4,
    app_update: AppsUpdateModel,
    db: Session = Depends(get_db),
    token: Dict[str, Any] = Security(token_verification.verify)
):
    try:
        app_to_update = db.query(Apps).filter(Apps.app_id == app_id).first()
        if not app_to_update:
            raise HTTPException(status_code=404, detail="App ikke funnet")

        if app_update.app_name is not None:
            app_to_update.app_name = app_update.app_name
        if app_update.app_owner is not None:
            app_to_update.app_owner = app_update.app_owner
        if app_update.is_active is not None:
            app_to_update.is_active = app_update.is_active

        db.commit()
        db.refresh(app_to_update)
        return app_to_update
    except Exception as e:
        db.rollback()
        logger.error(f"Kunne ikke oppdatere app: {e}")
        raise HTTPException(status_code=500, detail="Kunne ikke oppdatere app.")