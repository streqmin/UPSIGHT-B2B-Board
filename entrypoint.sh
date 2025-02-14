#!/bin/sh

# .env 파일 로드
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "Waiting for database to be ready..."
TIMEOUT=60
while ! pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "postgres"; do
  sleep 2
  TIMEOUT=$((TIMEOUT - 2))
  if [ "$TIMEOUT" -le 0 ]; then
    echo "Database did not become ready in time. Exiting."
    exit 1
  fi
done
echo "Database is ready!"

echo "Initializing database if needed..."
if [ ! -f /var/lib/postgresql/data/init_completed ]; then
  /init-db.sh
  touch /var/lib/postgresql/data/init_completed
else
  echo "Database already initialized, skipping."
fi

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn miniintern.wsgi:application --bind 0.0.0.0:8000 --workers=4 --timeout 120
