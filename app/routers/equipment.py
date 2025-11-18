from fastapi import APIRouter, Request, Depends, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.templates import templates
from services import equipment as svc

router = APIRouter(tags=["equipment"])

# GET localhost:8080/equipment/sensor
@router.get("/sensor", response_class=HTMLResponse)
def list_equipment_sensor_data(
    request: Request, db: Session = Depends(get_db)):
    
    # 장비 센서 데이터 목록 조회
    data = svc.list_equipment_sensor_data(db)
    return templates.TemplateResponse(
        "equipment_sensor_list.html",
        {"request": request, **data}    
    )

# POST localhost:8080/equipment/sensor
@router.post("/sensor")
def create_equipment_sensor_data(
    request: Request,
    db: Session = Depends(get_db), 
    data: dict = Body(...)
):
    # 장비 센서 데이터 등록   
    svc.create_equipment_sensor_data(request, db, data)
    
    return RedirectResponse(url="/equipment/sensor", status_code=303)