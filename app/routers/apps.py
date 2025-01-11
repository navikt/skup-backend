from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import UUID4
import logging
from ..database import get_db
from ..models import Apps
from ..schemas import AppsModel, AppsResponseModel, AppsUpdateModel

router = APIRouter()
logger = logging.getLogger(__name__)

# Create new app
@router.post("/api/apps", response_model=AppsModel, tags=["Apps"])
async def add_app(apps: AppsModel, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    new_app = Apps(
        app_name=apps.app_name,
        created_at=datetime.utcnow().replace(microsecond=0)
    )
    try:
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        return new_app
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to insert app: {e}")
        raise HTTPException(status_code=500, detail="Failed to add app.")

# Get all apps or filter by app_id or app_name (partial match)
@router.get("/api/apps", response_model=List[AppsResponseModel], tags=["Apps"])
async def get_apps(app_id: Optional[UUID4] = Query(None), app_name: Optional[str] = Query(None), db: Session = Depends(get_db)):
    try:
        query = db.query(Apps)
        if app_id:
            query = query.filter(Apps.app_id == app_id)
        if app_name:
            query = query.filter(Apps.app_name.like(f"%{app_name}%"))
        results = query.all()
        if not results:
            return []
        return [AppsResponseModel.from_orm(result) for result in results]
    except Exception as e:
        logger.error(f"Failed to fetch apps: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch apps.")

# Delete an app by app_id
@router.delete("/api/apps/{app_id}", response_model=AppsResponseModel, tags=["Apps"])
async def delete_app(app_id: UUID4, db: Session = Depends(get_db)):
    try:
        # Proceed to delete the app
        app_to_delete = db.query(Apps).filter(Apps.app_id == app_id).first()
        if not app_to_delete:
            raise HTTPException(status_code=404, detail="App not found")

        db.delete(app_to_delete)
        db.commit()
        return app_to_delete
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete app: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete app.")

# Update app details
@router.put("/api/apps/{app_id}", response_model=AppsResponseModel, tags=["Apps"])
async def update_app(app_id: UUID4, app_update: AppsUpdateModel, db: Session = Depends(get_db)):
    try:
        app_to_update = db.query(Apps).filter(Apps.app_id == app_id).first()
        if not app_to_update:
            raise HTTPException(status_code=404, detail="App not found")

        if app_update.app_name is not None:
            app_to_update.app_name = app_update.app_name
        if app_update.is_active is not None:
            app_to_update.is_active = app_update.is_active

        db.commit()
        db.refresh(app_to_update)
        return app_to_update
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update app: {e}")
        raise HTTPException(status_code=500, detail="Failed to update app.")