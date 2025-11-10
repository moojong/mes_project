from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from core.database import Base

class MasterEquipment(Base):
    __tablename__ = "master_equipment"

    equipment_id = Column(String(50), primary_key=True)                 
    name = Column(String(100), nullable=False)                          
    type = Column(String(50), nullable=True)                            
    operation_seq = Column(Integer, ForeignKey("master_operations.operation_seq"))  
    location = Column(String(100), nullable=True)
    enabled = Column(Boolean, default=True)