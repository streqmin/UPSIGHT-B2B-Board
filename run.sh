#!/bin/bash

# PostgreSQL 환경 변수 설정
export POSTGRES_DB="UPSIGHT"
export POSTGRES_USER="upsight"
export POSTGRES_PASSWORD="1q2w3e4r!"
export DATABASE_HOST="db"
export DATABASE_PORT="5432"

# Docker Compose 실행
docker-compose up -d
