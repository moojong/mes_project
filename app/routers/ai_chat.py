from fastapi import APIRouter, Request, Body, Form
from fastapi.responses import HTMLResponse

from core.templates import templates
from services import ai_chat as svc

router = APIRouter(tags=["ai_chat"])

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