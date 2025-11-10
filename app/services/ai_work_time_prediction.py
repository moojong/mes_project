import joblib
import numpy as np
import json
from pathlib import Path
import tensorflow as tf
from tensorflow import keras


class WorkTimePredictionService:
    
    def __init__(self, model_type='sklearn'):
        self.model_type = model_type
        self.model_dir = Path('ai_models/work_time')

        if model_type == 'sklearn':
            self._load_work_time_sklearn_model()
        elif model_type == 'tensorflow':
            self._load_work_time_tensorflow_model()
        else:
            raise ValueError(f"지원하지 않는 모델 타입: {model_type}")
        
        self.le_product = joblib.load(self.model_dir / 'label_encoder_product.pkl')
        self.le_equipment = joblib.load(self.model_dir / 'label_encoder_equipment.pkl')

    # Scikit-learn 모델 로드    
    def _load_work_time_sklearn_model(self):
        try:
            self.model = joblib.load(self.model_dir / 'rf_work_time_model.pkl')
            with open(self.model_dir / 'rf_work_time_model_info.json', 'r') as f:
                self.model_info = json.load(f)
            
            print("work_time_scikit_model 로드 완료")
        except Exception as e:
            raise RuntimeError(f"work_time_scikit_model 로드 실패: {e}")
    
    # TensorFlow 모델 로드    
    def _load_work_time_tensorflow_model(self):
        try:
            self.model = keras.models.load_model(self.model_dir / 'dnn_work_time_model.keras')
            self.scaler = joblib.load(self.model_dir / 'dnn_work_time_model_scaler.pkl')
            with open(self.model_dir / 'dnn_work_time_model_info.json', 'r') as f:
                self.model_info = json.load(f)

            print("work_time_tensorflow_model 로드 완료")
        except Exception as e:
            raise RuntimeError(f"work_time_tensorflow_model 로드 실패: {e}")
    
    def predict(self, product_id: str, operation_seq: int, 
                equipment_id: str, planned_qty: int) -> dict:

        try:
            # 인코딩
            product_encoded = self._encode_product(product_id)
            equipment_encoded = self._encode_equipment(equipment_id)

            # 입력 데이터 준비
            X = np.array([[product_encoded, operation_seq, equipment_encoded, planned_qty]])
            
            # 예측
            if self.model_type == 'sklearn':
                predicted_sec = self.model.predict(X)[0]
            else:  # tensorflow
                scaled_x = self.scaler.transform(X)
                predicted_sec = self.model.predict(scaled_x)[0][0]

            # 결과 반환
            return {
                'predicted_time_sec': round(float(predicted_sec), 2),
                'predicted_time_min': round(float(predicted_sec) / 60, 2),
                'model_type': self.model_type,
                'model_performance': {
                    'mae': self.model_info['mae'],
                    'rmse': self.model_info['rmse'],
                    'score': self.model_info['score']
                },
                'inputs': {
                    'product_id': product_id,
                    'operation_seq': operation_seq,
                    'equipment_id': equipment_id,
                    'planned_qty': planned_qty
                }
            }
        
        except Exception as e:
            raise RuntimeError(f"예측 실패: {e}")
    
    # 제품 ID Label Encoding    
    def _encode_product(self, product_id: str) -> int:
        try:
            return self.le_product.transform([product_id])[0]
        except ValueError:
            raise ValueError(f"알 수 없는 제품 ID: {product_id}")
    
    # 설비 ID Label Encoding
    def _encode_equipment(self, equipment_id: str) -> int:
        print("equipment_id:", equipment_id)
        try:
            return self.le_equipment.transform([equipment_id])[0]
        except ValueError:
            raise ValueError(f"알 수 없는 설비 ID: {equipment_id}")
    
    # 사용 가능한 제품 목록
    def get_available_products(self) -> list:
        return self.le_product.classes_.tolist()
    
    # 사용 가능한 설비 목록
    def get_available_equipments(self) -> list:
        return self.le_equipment.classes_.tolist()

    # 모델 정보 반환    
    def get_model_info(self) -> dict:
        return self.model_info


# 전역 서비스 인스턴스 (서버 시작시 한 번만 로드)
_work_time_sklearn_service = None
_work_time_tensorflow_service = None


def get_work_time_sklearn_service() -> WorkTimePredictionService:
    global _work_time_sklearn_service
    if _work_time_sklearn_service is None:
        _work_time_sklearn_service = WorkTimePredictionService(model_type='sklearn')
    return _work_time_sklearn_service


def get_work_time_tensorflow_service() -> WorkTimePredictionService:
    global _work_time_tensorflow_service
    if _work_time_tensorflow_service is None:
        _work_time_tensorflow_service = WorkTimePredictionService(model_type='tensorflow')
    return _work_time_tensorflow_service