from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, TEXT, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from core.database import Base

class QualityResult(Base):
    __tablename__ = "quality_results"

    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("quality_inspections.inspection_id"), nullable=False)
    inspector = Column(String(50), nullable=False)
    passed_qty = Column(Integer, nullable=False)
    defect_qty = Column(Integer, nullable=False)
    defect_code = Column(String(20), ForeignKey("master_defect_codes.defect_code"), nullable=False)
    defect_rate = Column(DECIMAL(5,2), nullable=True)
    start_ts = Column(DateTime, nullable=False)
    end_ts = Column(DateTime, nullable=False)
    inspection_time = Column(Integer, nullable=True) 
    notes = Column(TEXT, nullable=True)