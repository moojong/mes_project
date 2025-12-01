from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from core.templates import templates

router = APIRouter(tags=["image"])

# GET localhost:8080/image/classification
@router.get("/classification", response_class=HTMLResponse)
def show_classification(request: Request):
    return templates.TemplateResponse(
        "image_classification.html",
        {"request": request}
    )

# GET localhost:8080/image/detection
@router.get("/detection", response_class=HTMLResponse)
def show_detection(request: Request):
    return templates.TemplateResponse(
        "image_detection.html",
        {"request": request}
    )