from typing import Optional
from pydantic import BaseModel, UUID4, Field
from sqlalchemy import Boolean
from datetime import datetime

# Skjema for å opprette en ny app
class AppsModel(BaseModel):
    app_name: str

# Skjema for å oppdatere en eksisterende app
class AppsUpdateModel(BaseModel):
    app_name: Optional[str] = None
    is_active: Optional[bool] = None
    class Config:
         from_attributes = True

# Skjema for oppslagsmodellen til en app
class AppsResponseModel(BaseModel):
    app_id: UUID4
    app_name: str
    app_owner: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime
    class Config:
        from_attributes = True