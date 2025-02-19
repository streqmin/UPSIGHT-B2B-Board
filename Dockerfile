FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 생성
WORKDIR /code

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 의존성 설치
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 프로젝트 파일 복사
COPY . /code/

# 포트 노출
EXPOSE 8000

# 컨테이너 실행 시 entrypoint.sh 실행
ENTRYPOINT ["/code/entrypoint.sh"]
