from sqlalchemy import Column, Integer, String
from core.database import Base

class MasterOperation(Base):
    __tablename__ = "master_operations"

    operation_seq = Column(Integer, primary_key=True, autoincrement=False)  
    operation_name = Column(String(50), nullable=False)                     
    description = Column(String(255), nullable=True)