import joblib
import numpy as np
import json
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_


class ProductionQuantityPredictionService:
    
    def __init__(self, model_type='sklearn'):
        self.model_type = model_type
        self.model_dir = Path('ai_models/production_qty')

        if model_type == 'sklearn':
            self._load_production_qty_sklearn_model()
        elif model_type == 'tensorflow':
            self._load_production_qty_tensorflow_model()
        else:
            raise ValueError(f"지원하지 않는 모델 타입: {model_type}")

    # Scikit-learn 모델 로드    
    def _load_production_qty_sklearn_model(self):
        try:
            self.model = joblib.load(self.model_dir / 'lr_production_qty_model.pkl')
            with open(self.model_dir / 'lr_production_qty_model_info.json', 'r') as f:
                self.model_info = json.load(f)

            print("production_qty_sklearn_model 로드 완료")
        except Exception as e:
            raise RuntimeError(f"production_qty_sklearn_model 로드 실패: {e}")
    
    # TensorFlow 모델 로드    
    def _load_production_qty_tensorflow_model(self):
        try:
            self.model = keras.models.load_model(self.model_dir / 'dnn_production_qty_model.keras')
            self.scaler = joblib.load(self.model_dir / 'dnn_production_qty_model_scaler.pkl')
            with open(self.model_dir / 'dnn_production_qty_model_info.json', 'r') as f:
                self.model_info = json.load(f)

            print("production_qty_tensorflow_model 로드 완료")
        except Exception as e:
            raise RuntimeError(f"production_qty_tensorflow_model 로드 실패: {e}")

    def predict(self, db: Session, target_date: str) -> dict:

        try:
            # 인코딩
            date_obj = datetime.strptime(target_date, '%Y-%m-%d')

            # 일요일 체크
            if date_obj.weekday() == 6:
                raise ValueError("일요일은 생산하지 않습니다")

            # 시간 features 추출
            month = date_obj.month
            day = date_obj.day
            day_of_week = date_obj.weekday()  # 0=월, 5=토
            week_of_year = date_obj.isocalendar()[1]
            
            # 과거 생산 데이터 자동 조회
            past_production = self._get_past_production(db, date_obj)
            
            if len(past_production) < 6:
                raise ValueError(f"과거 생산 데이터 부족 (최소 6일 필요, 현재 {len(past_production)}일)")
            
            # Lag features 계산
            production_lag_1 = past_production[0]   # 전 영업일
            production_lag_6 = past_production[5]   # 6 영업일 전 (지난주 같은 요일)
            production_lag_12 = past_production[11] if len(past_production) > 11 else past_production[5]
            
            production_rolling_6 = np.mean(past_production[:6])
            production_rolling_24 = np.mean(past_production[:24]) if len(past_production) >= 24 else np.mean(past_production)
            
            production_trend_6 = (production_lag_1 - production_lag_6) / (production_lag_6)
            
            X = np.array([[
                month, day, day_of_week, week_of_year,
                # 과거 생산량
                production_lag_1,
                production_lag_6,
                production_lag_12,
                production_rolling_6,
                production_rolling_24,
                production_trend_6
            ]])
            
            # 예측
            if self.model_type == 'sklearn':
                predicted_qty = self.model.predict(X)[0]
            else:  # tensorflow
                scaled_x = self.scaler.transform(X)
                predicted_qty = self.model.predict(scaled_x)[0][0]

            # 결과 반환
            return {
                'predicted_production_qty': round(float(predicted_qty), 0),
                'target_date': target_date,
                'day_of_week': ['월', '화', '수', '목', '금', '토'][day_of_week],
                'model_type': self.model_type,
                'model_performance': {
                    'mae': self.model_info['mae'],
                    'rmse': self.model_info['rmse'],
                    'r2_score': self.model_info['score']
                },
                'past_production_data': {
                    'lag_1': float(production_lag_1),
                    'lag_6': float(production_lag_6),
                    'lag_12': float(production_lag_12),
                    'rolling_6': float(production_rolling_6),
                    'rolling_24': float(production_rolling_24),
                    'trend_6': float(production_trend_6)
                },
                'date_features': {
                    'month': month,
                    'day': day,
                    'week_of_year': week_of_year
                }
            }
        
        except Exception as e:
            raise RuntimeError(f"예측 실패: {e}")
    
    def _get_past_production(self, db: Session, target_date: datetime) -> list:

        from models.work_order import WorkOrder
        
        production_data = []
        current_date = target_date - timedelta(days=1) 
        
        # 최대 50일 전까지 조회 (영업일 24일 확보용)
        for _ in range(50):
            # 일요일 제외
            if current_date.weekday() != 6:
                # 해당 날짜 생산량 조회 (완료된 작업의 planned_qty 합계)
                daily_qty = db.query(
                    func.sum(WorkOrder.planned_qty)
                ).filter(
                    and_(
                        WorkOrder.status == 'S5_DONE',
                        func.date(WorkOrder.end_ts) == current_date.date()
                    )
                ).scalar()
                
                production_data.append(float(daily_qty) if daily_qty else 0.0)
                
                # 24개 영업일 확보되면 종료
                if len(production_data) >= 24:
                    break
            
            current_date -= timedelta(days=1)
        
        return production_data
    
    def predict_next_n_days(self, db: Session, start_date: str, n_days: int = 7) -> list:

        results = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(n_days):
            # 일요일은 건너뛰기
            if current_date.weekday() == 6:
                current_date += timedelta(days=1)
                continue
            
            try:
                result = self.predict(db, current_date.strftime('%Y-%m-%d'))
                results.append(result)
            except Exception as e:
                print(f"예측 실패 ({current_date.strftime('%Y-%m-%d')}): {e}")
            
            current_date += timedelta(days=1)
        
        return results
    
    
    # 모델 정보 반환    
    def get_model_info(self) -> dict:
        return self.model_info


# 전역 서비스 인스턴스 (서버 시작시 한 번만 로드)
_production_qty_sklearn_service = None
_production_qty_tensorflow_service = None


def get_production_qty_sklearn_service() -> ProductionQuantityPredictionService:
    global _production_qty_sklearn_service
    if _production_qty_sklearn_service is None:
        _production_qty_sklearn_service = ProductionQuantityPredictionService(model_type='sklearn')
    return _production_qty_sklearn_service


def get_production_qty_tensorflow_service() -> ProductionQuantityPredictionService:
    global _production_qty_tensorflow_service
    if _production_qty_tensorflow_service is None:
        _production_qty_tensorflow_service = ProductionQuantityPredictionService(model_type='tensorflow')
    return _production_qty_tensorflow_service