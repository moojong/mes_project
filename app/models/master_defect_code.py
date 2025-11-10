from sqlalchemy import Column, String, Boolean
from core.database import Base

class MasterDefectCode(Base):
    __tablename__ = "master_defect_codes"

    defect_code = Column(String(20), primary_key=True, index=True)  
    name = Column(String(100), nullable=False)                      
    description = Column(String(255), nullable=True)
    enabled = Column(Boolean, default=True)