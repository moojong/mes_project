# 베이스 이미지
FROM python:3.11-slim
# FROM mirror.gcr.io/library/python:3.11-slim

# 작업 디렉토리
WORKDIR /app

# 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사 (루트 전체 -> /app)
COPY . .

# (안전장치) 파이썬 모듈 검색 경로 보장
ENV PYTHONPATH=/app

# FastAPI 실행: app/main.py 안의 app 객체
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

