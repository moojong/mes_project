from sqlalchemy.orm import Session
from models.quality_inspection import QualityInspection
from models.quality_result import QualityResult
from models.master_defect_code import MasterDefectCode
from models.work_order import WorkOrder
from models.master_product import MasterProduct
from datetime import datetime

def list_inspections(db: Session):
    # 품질검사 목록 조회 (작업지시 및 제품 정보 포함)
    q = (
        db.query(
            QualityInspection.inspection_id,
            QualityInspection.order_id,
            QualityInspection.product_id,
            QualityInspection.inspection_qty,
            QualityInspection.inspector,
            QualityInspection.inspection_date,
            QualityInspection.status,
            QualityInspection.notes,
            MasterProduct.name.label("product_name"),
        )
        .join(MasterProduct, QualityInspection.product_id == MasterProduct.product_id)
        .order_by(QualityInspection.inspection_date.desc())
    )
    
    rows = q.all()
    
    items = []
    for r in rows:
        items.append({
            "inspection_id": str(r.inspection_id),
            "order_id": str(r.order_id),
            "product_id": r.product_id,
            "product_name": r.product_name,
            "inspection_qty": r.inspection_qty,
            "inspector": r.inspector,
            "inspection_date": r.inspection_date,
            "status": r.status,
            "notes": r.notes or "",
        })
    
    # 작업지시 목록 (검사 등록용)
    orders = db.query(WorkOrder).filter(WorkOrder.status == "S5_DONE").all()
    
    return {
        "items": items,
        "total": len(items),
        "orders": orders
    }

def create_inspection(db: Session, order_id: str, product_id: str, 
                     inspection_qty_raw: str, inspector: str, 
                     inspection_date_raw: str, notes: str):
    # 품질검사 등록
    inspection_qty = int(inspection_qty_raw)
    inspection_date = datetime.fromisoformat(inspection_date_raw).date()
    
    inspection = QualityInspection(
        order_id=order_id,
        product_id=product_id,
        inspection_qty=inspection_qty,
        inspector=inspector,
        inspection_date=inspection_date,
        notes=notes,
        status="PENDING"
    )
    
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection

def get_inspection_detail(db: Session, inspection_id: str):
    # 품질검사 상세 조회
    row = (
        db.query(
            QualityInspection.inspection_id,
            QualityInspection.order_id,
            QualityInspection.product_id,
            QualityInspection.inspection_qty,
            QualityInspection.inspector,
            QualityInspection.inspection_date,
            QualityInspection.status,
            QualityInspection.notes,
            QualityInspection.created_ts,
            MasterProduct.name.label("product_name"),
        )
        .join(MasterProduct, QualityInspection.product_id == MasterProduct.product_id)
        .filter(QualityInspection.inspection_id == inspection_id)
        .first()
    )
    
    if not row:
        return None
    
    return {
        "inspection_id": str(row.inspection_id),
        "order_id": str(row.order_id),
        "product_id": row.product_id,
        "product_name": row.product_name,
        "inspection_qty": row.inspection_qty,
        "inspector": row.inspector,
        "inspection_date": row.inspection_date,
        "status": row.status,
        "notes": row.notes or "",
        "created_ts": row.created_ts,
    }

def update_inspection(db: Session, inspection_id: str, inspection_qty_raw: str,
                     inspector: str, inspection_date_raw: str, notes: str):
    # 품질검사 수정
    inspection = db.query(QualityInspection).filter(
        QualityInspection.inspection_id == inspection_id
    ).first()
    
    if not inspection:
        return None
    
    inspection.inspection_qty = int(inspection_qty_raw)
    inspection.inspector = inspector
    inspection.inspection_date = datetime.fromisoformat(inspection_date_raw).date()
    inspection.notes = notes
    
    db.commit()
    db.refresh(inspection)
    return inspection

def delete_inspection(db: Session, inspection_id: str):
    # 품질검사 삭제
    inspection = db.query(QualityInspection).filter(
        QualityInspection.inspection_id == inspection_id
    ).first()
    
    if not inspection:
        return None
    
    db.delete(inspection)
    db.commit()
    return True

def list_results(db: Session):
    # 품질검사 결과 목록 조회
    q = (
        db.query(
            QualityResult.result_id,
            QualityResult.inspection_id,
            QualityResult.inspector,
            QualityResult.passed_qty,
            QualityResult.defect_qty,
            QualityResult.defect_code,
            QualityResult.defect_rate,
            QualityResult.start_ts,
            QualityResult.end_ts,
            QualityResult.inspection_time,
            MasterDefectCode.name.label("defect_name"),
            QualityInspection.product_id,
            MasterProduct.name.label("product_name"),
        )
        .join(QualityInspection, QualityResult.inspection_id == QualityInspection.inspection_id)
        .join(MasterProduct, QualityInspection.product_id == MasterProduct.product_id)
        .outerjoin(MasterDefectCode, QualityResult.defect_code == MasterDefectCode.defect_code)
        .order_by(QualityResult.start_ts.desc())
    )
    
    rows = q.all()
    
    items = []
    for r in rows:
        items.append({
            "result_id": str(r.result_id),
            "inspection_id": str(r.inspection_id),
            "inspector": r.inspector,
            "passed_qty": r.passed_qty,
            "defect_qty": r.defect_qty,
            "defect_code": r.defect_code,
            "defect_name": r.defect_name or "",
            "defect_rate": float(r.defect_rate) if r.defect_rate else 0.0,
            "product_id": r.product_id,
            "product_name": r.product_name,
            "start_ts": r.start_ts,
            "end_ts": r.end_ts,
            "inspection_time": r.inspection_time,
        })
    
    # 검사 목록 (결과 등록용)
    inspections = db.query(QualityInspection).filter(
        QualityInspection.status == "PENDING"
    ).all()
    
    # 불량 코드 목록
    defect_codes = db.query(MasterDefectCode).all()
    
    return {
        "items": items,
        "total": len(items),
        "inspections": inspections,
        "defect_codes": defect_codes
    }

def create_result(db: Session, inspection_id: str, inspector: str,
                 passed_qty_raw: str, defect_qty_raw: str, defect_code: str,
                 start_ts_raw: str, end_ts_raw: str, notes: str):
    # 품질검사 결과 등록
    passed_qty = int(passed_qty_raw)
    defect_qty = int(defect_qty_raw)
    start_ts = datetime.fromisoformat(start_ts_raw)
    end_ts = datetime.fromisoformat(end_ts_raw)
    
    # 불량률 계산
    total_qty = passed_qty + defect_qty
    defect_rate = (defect_qty / total_qty * 100) if total_qty > 0 else 0.0
    
    # 검사 소요시간 계산 (초)
    inspection_time = int((end_ts - start_ts).total_seconds())
    
    result = QualityResult(
        inspection_id=inspection_id,
        inspector=inspector,
        passed_qty=passed_qty,
        defect_qty=defect_qty,
        defect_code=defect_code if defect_code else None,
        defect_rate=defect_rate,
        start_ts=start_ts,
        end_ts=end_ts,
        inspection_time=inspection_time,
        notes=notes
    )
    
    db.add(result)
    
    # 검사 상태 업데이트
    inspection = db.query(QualityInspection).filter(
        QualityInspection.inspection_id == inspection_id
    ).first()
    if inspection:
        inspection.status = "COMPLETED"
    
    db.commit()
    db.refresh(result)
    return result