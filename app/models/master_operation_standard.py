from sqlalchemy import Column, String, Integer, ForeignKey, PrimaryKeyConstraint
from core.database import Base

class MasterOperationStandard(Base):
    __tablename__ = "master_operation_standards"

    product_id = Column(String(50), ForeignKey("master_products.product_id"), nullable=False)
    operation_seq = Column(Integer, ForeignKey("master_operations.operation_seq"), nullable=False)
    standard_cycle_time_sec = Column(Integer, nullable=False, default=0) 

    __table_args__ = (
        PrimaryKeyConstraint("product_id", "operation_seq", name="pk_operations_std"),
    )