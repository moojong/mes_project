from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.master_part import MasterPart
from models.part import Part

def get_part_spec(db: Session, part_name: str):
    """부품 정보 조회(부품명으로 사양 조회)"""
    q = (
        db.query(
            MasterPart.part_id,
            MasterPart.part_name,
            MasterPart.part_spec,
        )
        .filter(MasterPart.part_name == part_name)
        .first()
    )
    if not q:
        return None 
    
    return {
        "part_id": str(q.part_id),
        "part_spec": q.part_spec,
    }

def upload_part_file(db: Session, part_id: str, part_name: str, file_path: str, file_name: str):
    """부품 파일 업로드 정보 저장"""
    part = Part(
        master_part_id = part_id,
        part_name = part_name,
        file_path = file_path,
        file_name = file_name, 
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    return part