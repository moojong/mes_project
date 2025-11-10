from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.database import get_db 
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from core.templates import templates
from core.init_database import create_tables
from core.init_master_data import seed_master_data
# 라우터 등록
from routers import work
from routers import dashboard
from routers import quality

app = FastAPI(title="MES Project")


@app.on_event("startup")
def startup_event():
    create_tables()
    seed_master_data()
    print("데이터베이스 테이블 초기화 완료")
    from services.ai_production_qty_prediction import get_production_qty_sklearn_service, get_production_qty_tensorflow_service
    get_production_qty_sklearn_service()
    get_production_qty_tensorflow_service()
    from services.ai_work_time_prediction import get_work_time_sklearn_service, get_work_time_tensorflow_service
    get_work_time_sklearn_service()
    get_work_time_tensorflow_service()
    

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
	    "main.html", {"request": request, "title":"메인", "message":"FastAPI with Jinja2!"}
    )

@app.get("/health")
def health():
		# 해당 요청((http://localhost:8000/health/)에 대해 JSON 형식의 응답을 반환
    return {"status": "ok"}

# DB 헬스 체크 엔드포인트
@app.get("/db-health")
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))  # 연결 및 간단 쿼리
        return {"db": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="database error")



app.include_router(work.router, prefix="/work")
app.include_router(dashboard.router, prefix="/dashboard")
app.include_router(quality.router, prefix="/quality")