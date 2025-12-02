from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.database import get_db 
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from core.templates import templates
from core.init_database import create_tables
from core.init_master_data import seed_master_data
from core.load_ai_resource import setup_global_ai_assets
# 라우터 등록
from routers import work
from routers import dashboard
from routers import quality
from routers import equipment
from routers import image
from routers import part
from routers import ai_chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MES Project")
app.mount("/static", StaticFiles(directory="public"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경: 모든 origin 허용
    # allow_origins=["http://localhost:8000"],  # 프로덕션: 특정 origin만 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.on_event("startup")
def startup_event():
    create_tables()
    seed_master_data()
    setup_global_ai_assets(app)
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
app.include_router(equipment.router, prefix="/equipment")
app.include_router(image.router, prefix="/image")
app.include_router(part.router, prefix="/part")
app.include_router(ai_chat.router, prefix="/ai_chat")