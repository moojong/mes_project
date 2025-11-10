from core.database import Base, engine

# 생산관리 마스터
from models import master_product
from models import master_operation
from models import master_operation_standard
from models import master_equipment

# 품질관리 마스터
from models import master_defect_code
from models import master_inspection_item

from models.work_order import WorkOrder
from models.work_result import WorkResult

def create_tables():
    Base.metadata.create_all(bind=engine)