from fastapi import FastAPI
import joblib
import numpy as np
import json
from pathlib import Path
import tensorflow as tf
from tensorflow import keras

def setup_global_ai_assets(app: FastAPI):

    try:
        models_state = {}
        
        # DNN 모델 로드
        models_state["dnn_delivery_quality_model"] = keras.models.load_model("ai_models/delivery_quality/dnn_delivery_quality_model.keras")
        
        # 2. 스케일러/인코더 로드
        models_state["dnn_delivery_quality_scaler"] = joblib.load("ai_models/delivery_quality/dnn_delivery_quality_scaler.pkl")
        models_state["dnn_delivery_quality_encoder"] = joblib.load("ai_models/delivery_quality/dnn_delivery_quality_label.pkl")
        
        # 3. 모델 메타 정보 로드
        with open("ai_models/delivery_quality/dnn_delivery_quality_info.json", "r") as f:
            models_state["dnn_delivery_quality_info"] = json.load(f)

        # 로드된 전체 딕셔너리를 app.state에 저장
        app.state.ai_models = models_state
        
        print("AI 리소스 로드 완료.")
        
    except Exception as e:
        print(f"AI리소스 로드 실패: {e}")
