from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from core.database import Base

class QualityResult(Base):
    __tablename__ = "quality_results"
    
    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("quality_inspections.inspection_id"), nullable=False)
    inspector = Column(String(50), nullable=False)
    passed_qty = Column(Integer, nullable=False, default=0)
    defect_qty = Column(Integer, nullable=False, default=0)
    defect_code = Column(String(20), ForeignKey("master_defect_codes.defect_code"), nullable=True)
    defect_rate = Column(Numeric(5, 2), nullable=True)
    start_ts = Column(DateTime, nullable=False)
    end_ts = Column(DateTime, nullable=False)
    inspection_time = Column(Integer, nullable=True)
    notes = Column(String(500), nullable=True)