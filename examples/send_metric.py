#!/usr/bin/env python3
"""
Example script to send metrics to Theia agent
"""
import requests
import time
import random
from datetime import datetime

AGENT_URL = "http://localhost:8000"


def send_metric(name, value, tags=None, source=None):
    """Send a single metric to the agent"""
    payload = {
        "name": name,
        "value": value,
        "tags": tags or {},
        "timestamp": datetime.utcnow().isoformat(),
        "source": source or "example-client"
    }
    
    try:
        response = requests.post(f"{AGENT_URL}/metrics", json=payload)
        response.raise_for_status()
        print(f"✓ Sent metric: {name}={value}")
        return True
    except Exception as e:
        print(f"✗ Failed to send metric: {e}")
        return False


def simulate_button_clicks(num_clicks=10):
    """Simulate button click events"""
    print(f"Sending {num_clicks} button click metrics...")
    
    for i in range(num_clicks):
        send_metric(
            name="button_clicks",
            value=1,
            tags={"button": "submit", "page": "home"},
            source="web-app"
        )
        time.sleep(0.5)  # Wait 0.5 seconds between clicks


def simulate_api_requests(num_requests=5):
    """Simulate API request metrics"""
    print(f"Sending {num_requests} API request metrics...")
    
    endpoints = ["/api/users", "/api/products", "/api/orders"]
    
    for i in range(num_requests):
        endpoint = random.choice(endpoints)
        response_time = random.uniform(0.1, 2.0)
        
        send_metric(
            name="api_requests",
            value=response_time,
            tags={"endpoint": endpoint, "method": "GET"},
            source="api-server"
        )
        time.sleep(1)


if __name__ == "__main__":
    print("Theia Metric Sender Example")
    print("=" * 40)
    
    # Send some button clicks
    simulate_button_clicks(10)
    
    print("\n" + "-" * 40 + "\n")
    
    # Send some API request metrics
    simulate_api_requests(5)
    
    print("\n" + "=" * 40)
    print("Done! Check the dashboard at http://localhost:3000")

