# app/main.py

from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.database import get_db
from core.templates import templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from core.init_database import create_tables
from core.init_master_data import seed_master_data
from routers import work
from routers import dashboard

app = FastAPI(title="MES Project")

# 정적 파일 서빙(선택) — /static/style.css 등
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
	    "main.html",
	    {"request": request, "title":"메인", "message":"FastAPI with Jinja2!"}
    )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
def startup_event():
    create_tables()
    seed_master_data()
    print("데이터베이스 테이블 초기화 완료")

app.include_router(work.router, prefix="/work")
app.include_router(dashboard.router, prefix="/dashboard")
'''
@app.on_event("startup")
def startup_event():
    create_tables()
    seed_master_data()
    df_orders = generate_work_orders_csv(num_orders=500, output_dir="sample_data")
    df_results = generate_work_results_csv(df_orders, output_dir="sample_data")
    print("데이터베이스 테이블 초기화 완료")
    
    print("AI 모델 로드 중 ...")
    from services.ai_work_time_prediction import get_work_time_sklearn_service, get_work_time_tensorflow_service
    get_work_time_sklearn_service()
    get_work_time_tensorflow_service()
    
    from services.ai_production_qty_prediction import get_production_qty_sklearn_service, get_production_qty_tensorflow_service
    get_production_qty_sklearn_service()
    get_production_qty_tensorflow_service()
    
    print("AI 모델 로드 완료")
    '''