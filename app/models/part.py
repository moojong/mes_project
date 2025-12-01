from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from core.database import Base

class Part(Base):
    __tablename__ = "parts"
    
    part_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    master_part_id = Column(UUID(as_uuid=True), ForeignKey("master_parts.part_id"), nullable=False)
    part_name = Column(String(100), nullable=False)
    file_path = Column(String(200), nullable=True)
    file_name = Column(String(100), nullable=True)
    created_ts = Column(DateTime, nullable=False, default=datetime.utcnow)