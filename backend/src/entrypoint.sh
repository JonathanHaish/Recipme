#!/bin/bash
set -e

echo "Waiting for database..."
sleep 3

echo "Running migrations..."
python3 manage.py migrate --noinput

echo "Creating superuser if needed..."
python3 manage.py create_superuser_if_missing

echo "Starting server..."
exec python3 manage.py runserver 0.0.0.0:8000
