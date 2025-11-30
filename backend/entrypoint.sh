#!/bin/bash
set -e

echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

echo "Initializing database..."
python init_db.py

echo "Starting Flask application..."
exec python app.py

