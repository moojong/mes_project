from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.equipment_sensor_data import EquipmentSensorData

from datetime import datetime
from fastapi import Request

def list_equipment_sensor_data(request: Request, db: Session):
    """센서 데이터 목록 조회"""
    q = (
        db.query(
            EquipmentSensorData.sensor_id,
            EquipmentSensorData.timestamp,
            EquipmentSensorData.equipment_id,
            EquipmentSensorData.temperature,
            EquipmentSensorData.vibration,
            EquipmentSensorData.current,
            EquipmentSensorData.rpm,
            EquipmentSensorData.pressure,
            EquipmentSensorData.status,
        )
        .order_by(EquipmentSensorData.timestamp.desc())
    )

    rows = q.all()

    # 템플릿에서 쓰기 편하도록 dict 리스트로 변환
    items = []
    for r in rows:
        items.append({
            "sensor_id": r.sensor_id,
            "timestamp": r.timestamp,
            "equipment_id": r.equipment_id,
            "temperature": r.temperature,
            "vibration": r.vibration,
            "current": r.current,
            "rpm": r.rpm,
            "pressure": r.pressure,
            "status": r.status,
        })

    return {
        "items": items,
        "total": len(items),
    }

def create_equipment_sensor_data(Request, db: Session, data: dict):
    """센서 데이터 등록"""
    sensor_data = EquipmentSensorData(
        timestamp = data['timestamp'],
        equipment_id = data['equipment_id'],
        temperature = data['temperature'],
        vibration = data['vibration'],
        current = data['current'],
        rpm = data['rpm'],
        pressure = data['pressure'],
        
    )
    db.add(sensor_data)
    db.commit()
    db.refresh(sensor_data)
    
    return sensor_data