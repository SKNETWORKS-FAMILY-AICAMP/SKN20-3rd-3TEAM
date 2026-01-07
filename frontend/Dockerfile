# Frontend용 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Python 패키지 설치
COPY ./frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit 앱 복사
COPY ./frontend/streamlit_app.py .

# 환경변수
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8501

# Streamlit 실행
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
