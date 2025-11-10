from core.database import SessionLocal
# 생산관리 마스터
from models import master_product
from models import master_operation
from models import master_operation_standard
from models import master_equipment

# 품질관리 마스터
from models import master_defect_code
from models import master_inspection_item


def seed_master_data():
    """마스터 데이터 초기화 (존재 시 건너뜀)"""
    db = SessionLocal()
    try:
        # 1) 공정 단계
        operations = [
            {"operation_seq": 1, "operation_name": "부품준비", "description": "부품 트레이 적재"},
            {"operation_seq": 2, "operation_name": "조립",   "description": "부품 조립"},
            {"operation_seq": 3, "operation_name": "검사",   "description": "외관/기능 검사"},
            {"operation_seq": 4, "operation_name": "포장",   "description": "완성품 포장"},
            {"operation_seq": 5, "operation_name": "완료",   "description": "작업 완료"},
        ]
        for op in operations:
            exists = db.query(master_operation.MasterOperation).get(op["operation_seq"])
            if not exists:
                db.add(master_operation.MasterOperation(**op))
        db.commit()
        print(f"{len(operations)}개 공정 단계 생성 완료")

        # 2) 제품
        products = [
            {"product_id": "TEMP-100", "name": "온도 센서 모듈", "category": "SENSOR", "unit": "EA"},
            {"product_id": "PRES-200", "name": "압력 센서 모듈", "category": "SENSOR", "unit": "EA"},
            {"product_id": "GAS-300",  "name": "가스 센서 모듈", "category": "SENSOR", "unit": "EA"},
            {"product_id": "TEMP-101", "name": "온도 센서 모듈 (고정밀)", "category": "SENSOR", "unit": "EA"},
            {"product_id": "TEMP-102", "name": "온도 센서 모듈 (산업용)", "category": "SENSOR", "unit": "EA"},
            {"product_id": "PRES-201", "name": "압력 센서 모듈 (고압)", "category": "SENSOR", "unit": "EA"},
            {"product_id": "HUMID-400", "name": "습도 센서 모듈", "category": "SENSOR", "unit": "EA"},
            {"product_id": "MULTI-500", "name": "복합 센서 모듈 (온습도)", "category": "SENSOR", "unit": "EA"},
            {"product_id": "MULTI-501", "name": "복합 센서 모듈 (대기질)", "category": "SENSOR", "unit": "EA"},
        ]
        for p in products:
            exists = db.query(master_product.MasterProduct).get(p["product_id"])
            if not exists:
                db.add(master_product.MasterProduct(**p))
        db.commit()
        print(f"{len(products)}개 제품 생성 완료")

        # 3) 제품, 공정별 표준시간(초) 
        std_map = {
            "TEMP-100": {1: 15, 2: 40, 3: 25, 4: 10},   # 간단한 모델
            "PRES-200": {1: 20, 2: 50, 3: 35, 4: 15},   # 중간 복잡도
            "GAS-300": {1: 25, 2: 60, 3: 45, 4: 20},    # 복잡한 모델
            "TEMP-101": {1: 18, 2: 55, 3: 40, 4: 12},   # 고정밀 (검사 오래 걸림)
            "TEMP-102": {1: 22, 2: 65, 3: 30, 4: 18},   # 산업용 (조립 복잡)
            "PRES-201": {1: 25, 2: 70, 3: 50, 4: 20},   # 고압 (조립/검사 복잡)
            "HUMID-400": {1: 15, 2: 45, 3: 30, 4: 12},  # 습도 센서
            "MULTI-500": {1: 30, 2: 80, 3: 55, 4: 25},  # 복합 센서 (복잡)
            "MULTI-501": {1: 35, 2: 90, 3: 60, 4: 28},  # 대기질 (가장 복잡)
        }
        for pid, ops in std_map.items():
            for seq, sec in ops.items():
                exists = (db.query(master_operation_standard.MasterOperationStandard)
                            .filter(master_operation_standard.MasterOperationStandard.product_id == pid,
                                    master_operation_standard.MasterOperationStandard.operation_seq == seq)
                            .first())
                if not exists:
                    db.add(master_operation_standard.MasterOperationStandard(
                        product_id=pid, operation_seq=seq, standard_cycle_time_sec=sec
                    ))
        db.commit()
        print(f"{len(std_map)}개 제품의 공정별 표준시간 생성 완료")

        # 4) 설비(스테이션)
        equipments = [
            # 부품준비 공정 (operation_seq=1)
            {"equipment_id": "STN-PREP-1", "name": "부품준비 스테이션 1", "type": "부품준비", "operation_seq": 1, "location": "LINE-1"},
            {"equipment_id": "STN-PREP-2", "name": "부품준비 스테이션 2", "type": "부품준비", "operation_seq": 1, "location": "LINE-1"},
            {"equipment_id": "STN-PREP-3", "name": "부품준비 스테이션 3", "type": "부품준비", "operation_seq": 1, "location": "LINE-2"},
            
            # 조립 공정 (operation_seq=2)
            {"equipment_id": "STN-A", "name": "조립 스테이션 A", "type": "조립", "operation_seq": 2, "location": "LINE-1"},
            {"equipment_id": "STN-B", "name": "조립 스테이션 B", "type": "조립", "operation_seq": 2, "location": "LINE-1"},
            {"equipment_id": "STN-C", "name": "조립 스테이션 C", "type": "조립", "operation_seq": 2, "location": "LINE-2"},
            {"equipment_id": "STN-D", "name": "조립 스테이션 D (구형)", "type": "조립", "operation_seq": 2, "location": "LINE-2"},
            
            # 검사 공정 (operation_seq=3)
            {"equipment_id": "STN-INS-1", "name": "검사 스테이션 1 (자동)", "type": "검사", "operation_seq": 3, "location": "LINE-1"},
            {"equipment_id": "STN-INS-2", "name": "검사 스테이션 2 (자동)", "type": "검사", "operation_seq": 3, "location": "LINE-1"},
            {"equipment_id": "STN-INS-3", "name": "검사 스테이션 3 (수동)", "type": "검사", "operation_seq": 3, "location": "LINE-2"},
            
            # 포장 공정 (operation_seq=4)
            {"equipment_id": "STN-PKG-1", "name": "포장 스테이션 1", "type": "포장", "operation_seq": 4, "location": "LINE-1"},
            {"equipment_id": "STN-PKG-2", "name": "포장 스테이션 2", "type": "포장", "operation_seq": 4, "location": "LINE-1"},
            {"equipment_id": "STN-PKG-3", "name": "포장 스테이션 3", "type": "포장", "operation_seq": 4, "location": "LINE-2"},
        ]
        for e in equipments:
            exists = db.query(master_equipment.MasterEquipment).get(e["equipment_id"])
            if not exists:
                db.add(master_equipment.MasterEquipment(**e))
        db.commit()
        print(f"{len(equipments)}개 설비(스테이션) 생성 완료")

        # 5) 불량 코드
        defects = [
            {"defect_code": "D001", "name": "솔더 불량", "description": "솔더 브리징/미도포"},
            {"defect_code": "D002", "name": "센서 단선", "description": "리드 단선/접촉불량"},
            {"defect_code": "D003", "name": "외관 오염", "description": "스크래치/오염"},
            {"defect_code": "D004", "name": "부품 누락", "description": "필수 부품 미조립"},
            {"defect_code": "D005", "name": "감도 이상", "description": "센서 감도 규격 미달"},
            {"defect_code": "D006", "name": "응답시간 초과", "description": "반응 속도 지연"},
            {"defect_code": "D007", "name": "포장 불량", "description": "포장재 손상/미흡"},
            {"defect_code": "D008", "name": "라벨 오류", "description": "제품 라벨 누락/오기재"},
        ]
        for d in defects:
            exists = db.query(master_defect_code.MasterDefectCode).get(d["defect_code"])
            if not exists:
                db.add(master_defect_code.MasterDefectCode(**d))
        db.commit()
        print(f"{len(defects)}개 불량 코드 생성 완료")

        # 6) 품질 검사 항목 (허용범위 예시)
        items = [
            {"item_id": "SENSITIVITY", "name": "감도", "unit": "V", "lower_limit": 4.8, "upper_limit": 5.2, "target": 5.0},
            {"item_id": "RESP_TIME_MS", "name": "응답시간", "unit": "ms", "lower_limit": 0.0, "upper_limit": 120.0, "target": 100.0},
            {"item_id": "OFFSET_MV", "name": "오프셋", "unit": "mV", "lower_limit": -10.0, "upper_limit": 10.0, "target": 0.0},
            {"item_id": "ACCURACY", "name": "정확도", "unit": "%", "lower_limit": 98.0, "upper_limit": 102.0, "target": 100.0},
            {"item_id": "NOISE_LEVEL", "name": "노이즈레벨", "unit": "mV", "lower_limit": 0.0, "upper_limit": 5.0, "target": 2.0},
            {"item_id": "TEMP_COEFF", "name": "온도계수", "unit": "ppm/°C", "lower_limit": -50.0, "upper_limit": 50.0, "target": 0.0},
        ]
        for it in items:
            exists = db.query(master_inspection_item.MasterInspectionItem).get(it["item_id"])
            if not exists:
                db.add(master_inspection_item.MasterInspectionItem(**it))
        db.commit()
        print(f"{len(items)}개 품질 검사 항목 생성 완료")
        
        print("마스터 데이터 시딩 완료")
    finally:
        db.close()