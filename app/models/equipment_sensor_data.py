from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from core.database import Base


class EquipmentSensorData(Base):
    __tablename__ = "equipment_sensor_data"

    sensor_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False)
    equipment_id = Column(String(50), ForeignKey("master_equipment.equipment_id"), nullable=False)
    temperature = Column(Float, nullable=True)      # 온도 (°C)
    vibration = Column(Float, nullable=True)        # 진동
    current = Column(Float, nullable=True)          # 전류 (A)
    rpm = Column(Integer, nullable=True)            # RPM
    pressure = Column(Float, nullable=True)         # 압력 (bar)
    status = Column(Boolean, nullable=True)         # 상태 (0: 정상, 1: 이상)
