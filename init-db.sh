#!/bin/sh
set -e

echo "Waiting for database to be ready..."
TIMEOUT=60
while ! pg_isready -U "$DB_USER"; do
  echo "Waiting for PostgreSQL to start..."
  sleep 2
  TIMEOUT=$((TIMEOUT - 2))
  if [ "$TIMEOUT" -le 0 ]; then
    echo "Database did not start in time. Exiting."
    exit 1
  fi
done


echo "Database is ready!"
echo "Creating database and user if not exists..."

psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
    -- 사용자 생성 (존재하지 않을 경우)
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$POSTGRES_USER') THEN
            CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
        END IF;
    END
    \$\$;

    -- 데이터베이스 생성 (존재하지 않을 경우)
    SELECT 'CREATE DATABASE $POSTGRES_DB'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB')\gexec
