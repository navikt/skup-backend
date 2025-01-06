from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import Boolean
from .database import Base
from datetime import datetime

class Apps(Base):
    __tablename__ = "apps"

    app_id = Column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    app_name = Column(String)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)