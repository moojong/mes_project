# services/work_orders.py
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.work_order import WorkOrder
from models.work_result import WorkResult
from models.master_operation import MasterOperation
from models.master_equipment import MasterEquipment
from models.master_product import MasterProduct
from models.quality_inspection import QualityInspection
from models.quality_result import QualityResult
from datetime import datetime

from models.master_operation import MasterOperation
from models.master_equipment import MasterEquipment

def list_orders(db: Session):
    """작업지시 목록 조회 (제품 정보 포함)"""
    q = (
        db.query(
            WorkOrder.order_id,
            WorkOrder.product_id,
            WorkOrder.planned_qty,
            WorkOrder.status,
            WorkOrder.due_date,
            MasterProduct.name.label("product_name"),
        )
        .join(MasterProduct, WorkOrder.product_id == MasterProduct.product_id)
        .order_by(WorkOrder.due_date.asc())
    )

    rows = q.all()

    # 템플릿에서 쓰기 편하도록 dict 리스트로 변환
    items = []
    for r in rows:
        items.append({
            "order_id": r.order_id,
            "product_id": r.product_id,
            "product_name": r.product_name,
            "planned_qty": r.planned_qty,
            "status": r.status,
            "due_date": r.due_date,
        })

		# 제품 리스트 추가
    products = db.query(MasterProduct).order_by(MasterProduct.product_id).all()

    return {
        "items": items,
        "total": len(items),
        "products": products
    }

def create_order(db: Session, product_id: str, planned_qty_raw: str, due_date_raw: str):
    """작업지시 생성 (라우터에서 받은 원시 문자열을 변환/저장)"""
    planned_qty = int(planned_qty_raw)
    due_dt = datetime.fromisoformat(due_date_raw)  # 'YYYY-MM-DDTHH:MM' 형태 지원

    order = WorkOrder(
        product_id=product_id,
        planned_qty=planned_qty,
        due_date=due_dt,
        status="S0_PLANNED",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def get_order_detail(db: Session, order_id: str):
    """단일 작업지시 상세 조회 (제품명 포함)"""
    row = (
        db.query(
            WorkOrder.order_id,
            WorkOrder.product_id,
            WorkOrder.planned_qty,
            WorkOrder.status,
            WorkOrder.due_date,
            WorkOrder.created_ts,
            WorkOrder.start_ts,
            WorkOrder.end_ts,
            MasterProduct.name.label("product_name"),
        )
        .join(MasterProduct, WorkOrder.product_id == MasterProduct.product_id)
        .filter(WorkOrder.order_id == order_id)
        .first()
    )
    if not row:
        return None

    return {
        "order_id": row.order_id,
        "product_id": row.product_id,
        "product_name": row.product_name,
        "planned_qty": row.planned_qty,
        "status": row.status,
        "due_date": row.due_date,
        "created_ts": row.created_ts,
        "start_ts": row.start_ts,
        "end_ts": row.end_ts,
    }

def update_order(db: Session, order_id: str,
                 planned_qty_raw: str,
                 due_date_raw: str):
    """작업지시 수정"""
    order = db.query(WorkOrder).filter(WorkOrder.order_id == order_id).first()
    if not order: 
        return None

    order.planned_qty = int(planned_qty_raw)
    order.due_date = datetime.fromisoformat(due_date_raw)

    db.commit()
    db.refresh(order)
    return order

def delete_order(db: Session, order_id: str):
    """작업지시 삭제"""
    order = db.query(WorkOrder).filter(WorkOrder.order_id == order_id).first()
    if not order:
        return None

    db.delete(order)
    db.commit()
    return True

def list_results(db: Session):
    """
    생산실적 목록 조회 (공정/설비/제품 정보 포함)
    """
    q = (
        db.query(
            WorkResult.result_id,
            WorkResult.order_id,
            WorkResult.operation_seq,
            WorkResult.equipment_id,
            WorkResult.start_ts,
            WorkResult.end_ts,
            WorkOrder.product_id.label("product_id"),
            MasterProduct.name.label("product_name"),
            MasterOperation.operation_name.label("operation_name"),
            MasterEquipment.name.label("equipment_name"),
        )
        .join(WorkOrder, WorkResult.order_id == WorkOrder.order_id)
        .join(MasterOperation, WorkResult.operation_seq == MasterOperation.operation_seq)
        .outerjoin(MasterEquipment, WorkResult.equipment_id == MasterEquipment.equipment_id)
        .join(MasterProduct, WorkOrder.product_id == MasterProduct.product_id)
        .order_by(desc(WorkResult.start_ts))
    )

    rows = q.all()

    items = []
    for r in rows:
        items.append({
            "result_id": str(r.result_id),
            "order_id": str(r.order_id),
            "product_id": r.product_id,
            "product_name": r.product_name,
            "operation_seq": r.operation_seq,
            "operation_name": r.operation_name,
            "equipment_id": r.equipment_id,
            "equipment_name": r.equipment_name,
            "start_ts": r.start_ts,
            "end_ts": r.end_ts,
        })

    return {
        "items": items,
        "total": len(items),
    }

def list_progress(db: Session):
    """공정진행 페이지용 - 작업지시 목록 + 공정/설비 목록"""
    # 작업지시 목록 조회 (제품 이름 포함)
    q = (
        db.query(
            WorkOrder.order_id,
            WorkOrder.product_id,
            WorkOrder.planned_qty,
            WorkOrder.status,
            WorkOrder.due_date,
            MasterProduct.name.label("product_name"),
        )
        .join(MasterProduct, WorkOrder.product_id == MasterProduct.product_id)
        .order_by(WorkOrder.due_date.asc())
    )

    rows = q.all()

    # 템플릿에 쓰기 편한 dict 리스트로 변환
    items = []
    for r in rows:
        items.append({
            "order_id": r.order_id,
            "product_id": r.product_id,
            "product_name": r.product_name,
            "planned_qty": r.planned_qty,
            "status": r.status,
            "due_date": r.due_date,
        })

    # 공정 목록 (1~5 단계)
    operations = (
        db.query(
            MasterOperation.operation_seq,
            MasterOperation.operation_name,
        )
        .order_by(MasterOperation.operation_seq)
        .all()
    )

    # 설비 목록
    equipments = (
        db.query(
            MasterEquipment.equipment_id,
            MasterEquipment.name,
        )
        .filter(MasterEquipment.enabled == True)
        .order_by(MasterEquipment.equipment_id)
        .all()
    )

    return {
        "items": items,
        "total": len(items),
        "operations": operations,
        "equipments": equipments,
    }

# 단계 → 상태 매핑
STEP_TO_STATUS = {
    1: "S1_READY",
    2: "S2_ASSEMBLY",
    3: "S3_INSPECTION",
    4: "S4_PACK",
    5: "S5_DONE",
}

def advance_progress(db: Session, order_id: str, operation_seq: str, equipment_id: str | None):
    now = datetime.utcnow()
    op_seq = int(operation_seq) 

    # 주문 로드
    order = db.query(WorkOrder).filter(WorkOrder.order_id == order_id).first()

    # 실적 한 줄 추가
    wr = WorkResult(
        order_id=order_id,
        operation_seq=op_seq,
        equipment_id=equipment_id or None,
        start_ts=now,
        end_ts=now, # 단순 로직: start=end=now
    )
    db.add(wr)

    # 주문 상태/시간 갱신
    if order is not None:
        order.status = STEP_TO_STATUS.get(op_seq, order.status)
        if order.start_ts is None:
            order.start_ts = now
        if op_seq == 5:
            order.end_ts = now

    db.commit()

# def quailty_inspection_list(db: Session, order_id: str, operation_seq: str, equipment_id: str | None):