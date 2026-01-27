#!/bin/bash
set -e

echo "Fixing permissions for mounted volume..."
chown -R django:django /app

echo "Waiting for database..."
sleep 3

echo "Running migrations..."
su django -c "python3 manage.py migrate --noinput"

echo "Collecting static files..."
su django -c "python3 manage.py collectstatic --noinput"

echo "Creating superuser if needed..."
su django -c "python3 manage.py create_superuser_if_missing"

echo "Starting gunicorn server..."
exec su django -c "gunicorn mysite.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -"
