from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from core.database import Base

class MasterPart(Base):
    __tablename__ = "master_parts"
    
    part_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_name = Column(String(100), nullable=False)
    part_spec = Column(String(200), nullable=True)