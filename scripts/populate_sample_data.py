#!/usr/bin/env python3
"""
Script to populate InfluxDB with sample metrics data for testing
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add backend directory to path to import app modules
# When running in Docker, backend is at /app, scripts are at /scripts
if os.path.exists("/app"):
    # Running in Docker
    sys.path.insert(0, "/app")
else:
    # Running locally
    backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

from influxdb_service import InfluxDB


def populate_sample_data():
    """Populate InfluxDB with sample metrics"""
    influxdb = InfluxDB()

    print("Populating sample metrics data...")

    # Generate metrics for the last 6 hours to have more data points
    now = datetime.utcnow()
    start_time = now - timedelta(hours=6)

    metrics_count = 0

    # Button clicks - high frequency
    print("Generating button click metrics...")
    for i in range(50):
        timestamp = start_time + timedelta(
            seconds=random.randint(0, 21600)  # Random time in last 6 hours
        )
        influxdb.write_metric(
            name="button_clicks",
            value=random.randint(200, 1500),
            tags={
                "button": random.choice(["submit", "cancel", "save", "delete", "edit"]),
                "page": random.choice(["home", "dashboard", "settings", "profile"]),
            },
            timestamp=timestamp,
            source="web-app",
        )
        metrics_count += 1

    # API requests - medium frequency with response times
    print("Generating API request metrics...")
    endpoints = ["/api/users", "/api/products", "/api/orders", "/api/auth", "/api/search"]
    methods = ["GET", "POST", "PUT", "DELETE"]

    for i in range(40):
        timestamp = start_time + timedelta(seconds=random.randint(0, 21600))
        influxdb.write_metric(
            name="api_requests",
            value=random.uniform(0.05, 2.5),  # Response time in seconds
            tags={
                "endpoint": random.choice(endpoints),
                "method": random.choice(methods),
                "status": random.choice(["200", "201", "400", "404", "500"]),
            },
            timestamp=timestamp,
            source="api-server",
        )
        metrics_count += 1

    # Page views - high frequency
    print("Generating page view metrics...")
    pages = ["/", "/dashboard", "/products", "/about", "/contact", "/login"]

    for i in range(60):
        timestamp = start_time + timedelta(seconds=random.randint(0, 21600))
        influxdb.write_metric(
            name="page_views",
            value=random.randint(200, 1500),
            tags={
                "page": random.choice(pages),
                "user_type": random.choice(["guest", "authenticated", "admin"]),
            },
            timestamp=timestamp,
            source="web-app",
        )
        metrics_count += 1

    # Error counts - lower frequency
    print("Generating error metrics...")
    error_types = ["database_error", "network_error", "validation_error", "auth_error"]

    for i in range(15):
        timestamp = start_time + timedelta(seconds=random.randint(0, 21600))
        influxdb.write_metric(
            name="errors",
            value=random.randint(1, 5),
            tags={
                "error_type": random.choice(error_types),
                "severity": random.choice(["low", "medium", "high", "critical"]),
            },
            timestamp=timestamp,
            source="api-server",
        )
        metrics_count += 1

    # CPU usage - continuous metric
    print("Generating CPU usage metrics...")
    for i in range(30):
        timestamp = start_time + timedelta(seconds=random.randint(0, 21600))
        influxdb.write_metric(
            name="cpu_usage",
            value=random.uniform(10.0, 95.0),  # CPU percentage
            tags={
                "server": random.choice(["web-1", "web-2", "api-1", "api-2"]),
                "region": random.choice(["us-east", "us-west", "eu-central"]),
            },
            timestamp=timestamp,
            source="monitoring-agent",
        )
        metrics_count += 1

    # Memory usage
    print("Generating memory usage metrics...")
    for i in range(30):
        timestamp = start_time + timedelta(seconds=random.randint(0, 21600))
        influxdb.write_metric(
            name="memory_usage",
            value=random.uniform(40.0, 90.0),  # Memory percentage
            tags={
                "server": random.choice(["web-1", "web-2", "api-1", "api-2"]),
                "region": random.choice(["us-east", "us-west", "eu-central"]),
            },
            timestamp=timestamp,
            source="monitoring-agent",
        )
        metrics_count += 1

    # Database query time
    print("Generating database query metrics...")
    for i in range(25):
        timestamp = start_time + timedelta(seconds=random.randint(0, 21600))
        influxdb.write_metric(
            name="db_query_time",
            value=random.uniform(0.01, 0.5),  # Query time in seconds
            tags={
                "query_type": random.choice(["SELECT", "INSERT", "UPDATE", "DELETE"]),
                "table": random.choice(["users", "products", "orders", "metrics"]),
            },
            timestamp=timestamp,
            source="database",
        )
        metrics_count += 1

    influxdb.close()

    print(f"✓ Successfully inserted {metrics_count} sample metrics!")
    print("\nSample metrics created:")
    print("  - button_clicks: 50 metrics")
    print("  - api_requests: 40 metrics")
    print("  - page_views: 60 metrics")
    print("  - errors: 15 metrics")
    print("  - cpu_usage: 30 metrics")
    print("  - memory_usage: 30 metrics")
    print("  - db_query_time: 25 metrics")
    print("\nTotal: 250 metrics")
    print("\nRefresh your frontend dashboard to see the metrics!")


if __name__ == "__main__":
    populate_sample_data()
