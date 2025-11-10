from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.templates import templates
from services import work as svc

router = APIRouter(tags=["work"])

@router.get("/orders", response_class=HTMLResponse)
def list_orders(request: Request, db: Session = Depends(get_db)):
		# services/work.py 의 list_orders 함수 호출
    data = svc.list_orders(db)

    # orders_list.html에 request, data 변수를 전달하여 최종 HTML 문서를 완성
    return templates.TemplateResponse(
        "orders_list.html",
        {"request": request, **data}
    )

@router.post("/orders")
def create_order(
    db: Session = Depends(get_db),
    product_id: str = Form(...),
    planned_qty: str = Form(...),   # 서비스에서 int로 변환
    due_date: str = Form(...),      # 서비스에서 datetime으로 변환
):
    svc.create_order(db, product_id, planned_qty, due_date)
    return RedirectResponse(url="/work/orders", status_code=303)

@router.get("/orders/{order_id}", response_class=HTMLResponse)
def order_detail(order_id: str, request: Request, db: Session = Depends(get_db)):
    data = svc.get_order_detail(db, order_id)
    if not data:
        return HTMLResponse("Order not found", status_code=404)
    # 템플릿에 request와 상세 데이터 전달
    return templates.TemplateResponse(
        "orders_detail.html", 
        {"request": request, **data}
    )

@router.post("/orders/{order_id}/update")
def order_update(order_id: str,
                 planned_qty: str = Form(...),
                 due_date: str = Form(...),
                 db: Session = Depends(get_db)):
    updated = svc.update_order(
                                db, 
                                order_id, 
                                planned_qty_raw=planned_qty, 
                                due_date_raw=due_date, 
                            )
    if not updated:
        return HTMLResponse("Order not found", status_code=404)
    return RedirectResponse(url=f"/work/orders/", status_code=303)

@router.post("/orders/{order_id}/delete")
def order_delete(order_id: str, db: Session = Depends(get_db)):
    deleted = svc.delete_order(db, order_id)
    if not deleted:
        return HTMLResponse("Order not found", status_code=404)
    return RedirectResponse(url="/work/orders", status_code=303)    

@router.get("/results", response_class=HTMLResponse)
def list_results(request: Request, db: Session = Depends(get_db)):
    # services/work.py 의 list_results 함수 호출
    data = svc.list_results(db)
    # results_list.html에 request, data 변수를 전달하여 최종 HTML 문서를 완성
    return templates.TemplateResponse(
        "results_list.html",
        {"request": request, **data}
    )


@router.get("/progress", response_class=HTMLResponse)
def list_progress(request: Request, db: Session = Depends(get_db)):
		# services/work.py 의 list_progress 함수 호출
    data = svc.list_progress(db)
    # progress_list.html에 request, data 변수를 전달하여 최종 HTML 문서를 완성
    return templates.TemplateResponse(
        "progress_list.html",
        {"request": request, **data}
    )    

@router.post("/progress")
def advance_progress(
    db: Session = Depends(get_db),
    order_id: str = Form(...),
    operation_seq: str = Form(...),
    equipment_id: str = Form(None)
):
    svc.advance_progress(db, order_id, operation_seq, equipment_id)
    return RedirectResponse(url="/work/progress", status_code=303)