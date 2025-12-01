#!/bin/bash
set -e

# If arguments are provided (e.g., celery command), skip InfluxDB check and execute directly
if [ $# -gt 0 ]; then
    exec "$@"
fi

echo "Waiting for InfluxDB to be ready..."
while ! /usr/bin/curl -s http://influxdb:8086/health > /dev/null; do
  sleep 0.5
done
echo "InfluxDB is ready!"

echo "Starting Flask application..."
exec python app.py

