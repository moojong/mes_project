from fastapi import APIRouter, Request, Body, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse

from core.templates import templates
from services import ai_chat as svc

from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter(tags=["ai_chat"])

@router.get("/text_to_sql", response_class=HTMLResponse)
async def show_text_to_sql(request: Request):
    return templates.TemplateResponse(
        "text_to_sql.html",
        {"request": request}
    )

@router.post("/text_to_sql", response_class=HTMLResponse)
async def text_to_sql_chat(
    request: Request,
    question: str = Form(...),
    model: str = Form(...),
    db: Session = Depends(get_db),
):
    # 1) 자연어 -> SQL 생성
    sql = svc.generate_sql_from_text(db, question, model)

    # 2) SQL 실행
    exec_result = svc.execute_generated_sql(db, sql)

    context = {
        "request": request,
        "question": question,
        "sql": sql,
        "selected_model": model,
        "result": exec_result,
    }
    return templates.TemplateResponse("text_to_sql.html", context)

@router.get("/rag", response_class=HTMLResponse)
async def show_rag_page(request: Request):
    return templates.TemplateResponse("rag.html", {"request": request})

@router.post("/rag/upload", response_class=HTMLResponse)
async def upload_rag_document(
    request: Request,
    upload_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    result = await svc.process_document_and_store_vectors(db=db, upload_file=upload_file)

    return templates.TemplateResponse("rag.html", {
        "request": request,
        "upload_result": result,
    })

@router.post("/rag/chat", response_class=HTMLResponse)
async def rag_chat(
    request: Request,
    user_input: str = Form(...),
    model: str = Form(...),
    db: Session = Depends(get_db)
):
    response = svc.generate_rag_response(db, user_input, model)

    return templates.TemplateResponse("rag.html", {
        "request": request,
        "user_input": user_input,
        "response": response,
        "selected_model": model
    })

# GET localhost:8080/ai_chat/llama
@router.get("/llama", response_class=HTMLResponse)
def show_llama_chat(request: Request):
    return templates.TemplateResponse(
        "llama_chat.html",
        {"request": request}
    )

# POST localhost:8000/ai_chat/llama
@router.post("/llama")
def generate_response_llama_chat(
    data: dict = Body(...)
):
	
    response = svc.generate_response(data)
    
    return {"reply": response}

@router.get("/chatbot", response_class=HTMLResponse)
async def show_chatbot(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

@router.post("/chatbot", response_class=HTMLResponse)
async def process_chatbot(
    request: Request, 
    user_input: str = Form(...),
    model: str = Form(...)
):
    messages = [{"role": "user", "content": user_input}]
    
    if model == "gpt":
        response = svc.generate_gpt_chat_response(messages)
    elif model == "gemini":
        response = svc.generate_gemini_chat_response(messages)
    elif model == "qwen2.5:7b" or model == "gemma3:4b":
        response = svc.generate_local_llm_chat_response(model, messages)
    else:
        response = "Invalid model selected."
    
    return templates.TemplateResponse("chatbot.html", {
      "request": request, 
	    "user_input": user_input, 
	    "response": response,
      "selected_model": model
	})