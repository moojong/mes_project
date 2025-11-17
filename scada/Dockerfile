FROM python:3.11-slim

WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 시뮬레이터 코드 복사
COPY simulator.py .

# CSV 데이터 디렉토리
COPY data/ ./data/

# 실행
CMD ["python", "simulator.py"]