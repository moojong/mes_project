from sqlalchemy import Column, String, Boolean, Float
from core.database import Base

class MasterInspectionItem(Base):
    __tablename__ = "master_inspection_items"

    item_id = Column(String(50), primary_key=True, index=True)      
    name = Column(String(100), nullable=False)                      
    unit = Column(String(20), default="")                           
    lower_limit = Column(Float, nullable=True)                      
    upper_limit = Column(Float, nullable=True)                      
    target = Column(Float, nullable=True)                           
    enabled = Column(Boolean, default=True)