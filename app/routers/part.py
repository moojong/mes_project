from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from core.database import get_db
from services import part as svc
from pathlib import Path
import uuid
import shutil

UPLOAD_DIR = Path("uploads")

router = APIRouter(tags=["part"])

# GET localhost:8080/part/spec/{part_name}
@router.get("/spec/{part_name}")
def get_spec(part_name: str, db=Depends(get_db)):
    part = svc.get_part_spec(db, part_name)
    return {"part_id": part["part_id"], "part_spec": part["part_spec"]}

@router.post("/upload")
async def upload_part(
    db=Depends(get_db),
    file: UploadFile = File(),
    part_id: str = Form(),
    part_name: str = Form(),
):
    file_name = file.filename
    unique_filename = f"{uuid.uuid4()}_{file_name}"
    
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        with file_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        file.file.close()  
    
    svc.upload_part_file(db, part_id, part_name, file_path=str(file_path), file_name=file_name)
    return {"status": "success"}
