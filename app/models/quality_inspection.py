from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, TEXT
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from core.database import Base


class QualityInspection(Base):
    __tablename__ = "quality_inspections"

    inspection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("work_orders.order_id"), nullable=False)
    product_id = Column(String(50), ForeignKey("master_products.product_id"), nullable=False)
    inspection_qty = Column(Integer, nullable=False)
    inspector = Column(String(50), nullable=True)
    inspection_date = Column(DateTime, nullable=False) 
    status = Column(String(20), default="PENDING")
    notes = Column(TEXT, nullable=True)
    created_ts = Column(DateTime, nullable=True)