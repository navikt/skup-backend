from typing import Optional
from pydantic import BaseModel, UUID4, Field
from sqlalchemy import Boolean
from datetime import datetime

class AppsModel(BaseModel):
    app_name: str

class AppsUpdateModel(BaseModel):
    app_name: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
         from_attributes = True

class AppsResponseModel(BaseModel):
    app_id: UUID4
    app_name: str
    app_owner: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime

    class Config:
        from_attributes = True