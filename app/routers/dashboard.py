from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.templates import templates
from services import dashboard as svc
from services.ai_production_qty_prediction import get_production_qty_sklearn_service, get_production_qty_tensorflow_service

router = APIRouter(tags=["dashboard"])

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    # 대시보드 페이지
    data = svc.get_dashboard_data(db)
    # 생산량 AI 예측(sklearn 모델 사용)
    production_qty_service = get_production_qty_sklearn_service()
    #tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = "2025-09-01"
    prediction = production_qty_service.predict(db, tomorrow)
    
    data['prediction'] = prediction
        
    print(f"생산량 AI 예측 결과 ({tomorrow}):", prediction)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, **data}
    )
