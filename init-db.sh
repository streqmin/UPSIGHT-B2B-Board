#!/bin/sh
set -e

echo "Initializing database if needed..."

COUNT_TIME=0
until pg_isready -U $POSTGRES_USER; do
  echo "Waiting for PostgreSQL to start...$COUNT_TIME"
  sleep 1
  COUNT_TIME=$((COUNT_TIME + 1))
done

# psql 내부에서 직접 SQL 실행
psql -U $POSTGRES_USER <<-EOSQL
    DO \$\$
    BEGIN
        -- 데이터베이스 생성 (존재하지 않을 경우)
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}') THEN
            CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};
            GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};
        END IF;
    END
    \$\$;
EOSQL

echo "Database initialization completed."
