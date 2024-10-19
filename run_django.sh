#!/bin/bash

# 필요한 패키지 설치
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 환경 변수 설정 (필요 시, 실제 값으로 변경하세요)
export POSTGRES_DB="UPSIGHT"
export POSTGRES_USER="upsight"
export POSTGRES_PASSWORD="1q2w3e4r!"
export DATABASE_HOST="localhost"
export DATABASE_PORT="5432"

# 데이터베이스 마이그레이션
echo "Running migrations..."
python manage.py migrate

# Django 서버 실행
echo "Starting Django development server..."
python manage.py runserver
