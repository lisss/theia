#!/bin/bash
# Script to populate sample data using Docker

echo "Populating sample metrics data..."
docker-compose exec backend python /scripts/populate_sample_data.py

