#!/bin/bash
set -e

echo "Waiting for database..."
sleep 3

echo "Running migrations..."
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Creating superuser if needed..."
python3 manage.py create_superuser_if_missing

echo "Starting gunicorn server..."
exec /home/django/.local/bin/gunicorn mysite.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
