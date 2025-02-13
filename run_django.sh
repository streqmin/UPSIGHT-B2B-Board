#!/bin/bash

# 필요한 패키지 설치
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 데이터베이스 마이그레이션
echo "Running migrations..."
python manage.py migrate

# Django 서버 실행
echo "Starting Django development server..."
python manage.py runserver
