from sqlalchemy import Column, String, Boolean
from core.database import Base

class MasterProduct(Base):
    __tablename__ = "master_products"

    product_id = Column(String(50), primary_key=True, index=True)  
    name = Column(String(100), nullable=False)                     
    category = Column(String(50), nullable=True)                   
    unit = Column(String(20), default="EA")                        
    enabled = Column(Boolean, default=True)