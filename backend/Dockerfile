# Backend용 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY ./backend/app /app/app

# src 폴더 복사 (ensemble.py 등)
COPY ./src /app/src

# 환경변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 포트 노출
EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
