import pandas as pd
import requests
import time
import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# 환경 변수
SERVER_URL = os.getenv("SERVER_URL", "http://server:8000")
ENDPOINT = f"{SERVER_URL}/equipment/sensor"
INTERVAL = int(os.getenv("INTERVAL", "10"))  # 초 단위
CSV_PATH = "/app/data/equipment_sensor_data.csv"

def main():
    logger.info("SCADA 시뮬레이터 시작")
    logger.info(f"서버 URL: {SERVER_URL}")
    logger.info(f"전송 간격: {INTERVAL}초")
    
    # 서버 연결 대기
    time.sleep(5)
    
    # CSV 데이터 로드
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        logger.error(f"CSV 파일 로드 실패: {e}")
        return

    # 데이터 전송
    for _, row in df.iterrows():
        payload = {
            "timestamp": datetime.now(ZoneInfo("Asia/Seoul")).strftime('%Y-%m-%d %H:%M:%S'),
            "equipment_id": row["equipment_id"],
            "temperature": row["temperature"],
            "vibration": row["vibration"],
            "current": row["current"],
            "rpm": row["rpm"],
            "pressure": row["pressure"]
        }
        logger.info(payload)
        try:
            response = requests.post(ENDPOINT, json=payload)
            response.raise_for_status()
            logger.info(f"Sent data for {payload['equipment_id']} at {payload['timestamp']}")
        except requests.RequestException as e:
            logger.error(f"Failed to send data: {e}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("시뮬레이터 종료")
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        raise