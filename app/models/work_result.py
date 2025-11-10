from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from core.database import Base


class WorkResult(Base):
    __tablename__ = "work_results"

    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("work_orders.order_id"), nullable=False)
    operation_seq = Column(Integer, ForeignKey("master_operations.operation_seq"), nullable=False)
    equipment_id = Column(String(50), ForeignKey("master_equipment.equipment_id"), nullable=True)

    start_ts = Column(DateTime, nullable=False)
    end_ts = Column(DateTime, nullable=False)