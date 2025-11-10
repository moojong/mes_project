from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.templates import templates
from services import quality as svc

router = APIRouter(tags=["quality"])

# GET localhost:8080/quality/inspections
@router.get("/inspections", response_class=HTMLResponse)
def list_inspections(request: Request, db: Session = Depends(get_db)):
    # 품질검사 목록 조회
    data = svc.list_inspections(db)
    return templates.TemplateResponse(
        "inspections_list.html",
        {"request": request, **data}
    )

# POST localhost:8080/quality/inspections
@router.post("/inspections")
def create_inspection(
    db: Session = Depends(get_db),
    order_id: str = Form(...),
    product_id: str = Form(...),
    inspection_qty: str = Form(...),
    inspector: str = Form(...),
    inspection_date: str = Form(...),
    notes: str = Form("")
):
    # 품질검사 등록
    svc.create_inspection(db, order_id, product_id, inspection_qty, 
                         inspector, inspection_date, notes)
    return RedirectResponse(url="/quality/inspections", status_code=303)

# GET localhost:8080/quality/inspections/{inspection_id}
@router.get("/inspections/{inspection_id}", response_class=HTMLResponse)
def inspection_detail(inspection_id: str, request: Request, db: Session = Depends(get_db)):
    # 품질검사 상세 조회
    data = svc.get_inspection_detail(db, inspection_id)
    if not data:
        return HTMLResponse("Inspection not found", status_code=404)
    return templates.TemplateResponse(
        "inspections_detail.html",
        {"request": request, **data}
    )

# POST localhost:8080/quality/inspections/{inspection_id}/update
@router.post("/inspections/{inspection_id}/update")
def inspection_update(
    inspection_id: str,
    inspection_qty: str = Form(...),
    inspector: str = Form(...),
    inspection_date: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    # 품질검사 수정
    updated = svc.update_inspection(db, inspection_id, inspection_qty, 
                                   inspector, inspection_date, notes)
    if not updated:
        return HTMLResponse("Inspection not found", status_code=404)
    return RedirectResponse(url="/quality/inspections", status_code=303)

# POST localhost:8080/quality/inspections/{inspection_id}/delete
@router.post("/inspections/{inspection_id}/delete")
def inspection_delete(inspection_id: str, db: Session = Depends(get_db)):
    # 품질검사 삭제
    deleted = svc.delete_inspection(db, inspection_id)
    if not deleted:
        return HTMLResponse("Inspection not found", status_code=404)
    return RedirectResponse(url="/quality/inspections", status_code=303)

# GET localhost:8080/quality/results
@router.get("/quality_results", response_class=HTMLResponse)
def list_results(request: Request, db: Session = Depends(get_db)):
    # 품질검사 결과 목록 조회
    data = svc.list_results(db)
    return templates.TemplateResponse(
        "quality_results_list.html",
        {"request": request, **data}
    )

# POST localhost:8080/quality/results
@router.post("/quality_results")
def create_result(
    db: Session = Depends(get_db),
    inspection_id: str = Form(...),
    inspector: str = Form(...),
    passed_qty: str = Form(...),
    defect_qty: str = Form(...),
    defect_code: str = Form(""),
    start_ts: str = Form(...),
    end_ts: str = Form(...),
    notes: str = Form("")
):
    # 품질검사 결과 등록
    svc.create_result(db, inspection_id, inspector, passed_qty, 
                     defect_qty, defect_code, start_ts, end_ts, notes)
    return RedirectResponse(url="/quality/results", status_code=303)