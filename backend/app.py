from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

from influxdb_service import InfluxDB

influxdb = InfluxDB()


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """Get metrics with optional filtering"""
    name = request.args.get("name")
    source = request.args.get("source")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    limit = request.args.get("limit", type=int, default=1000)

    metrics = influxdb.query_metrics(
        name=name, source=source, start_time=start_time, end_time=end_time, limit=limit
    )

    return jsonify(metrics)


@app.route("/api/metrics/aggregate", methods=["GET"])
def get_aggregated_metrics():
    """Get aggregated metrics grouped by name and time window"""
    name = request.args.get("name")
    window = request.args.get("window", "1h")
    aggregate_fn = request.args.get("aggregate", "mean")  # mean, sum, max, min, count

    metrics = influxdb.query_aggregated_metrics(name=name, window=window, aggregate_fn=aggregate_fn)

    return jsonify(metrics)


@app.route("/api/metrics/names", methods=["GET"])
def get_metric_names():
    """Get list of all unique metric names"""
    names = influxdb.get_metric_names()
    return jsonify(names)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    try:
        influxdb.client.ping()
        return jsonify({"status": "healthy"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


def init_db():
    """Check InfluxDB connection"""
    max_retries = 30
    retry_count = 0

    while retry_count < max_retries:
        try:
            influxdb.client.ping()
            print("InfluxDB connection successful!")
            return True
        except Exception as e:
            retry_count += 1
            print(f"InfluxDB connection failed (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(2)
            else:
                print("Failed to connect to InfluxDB after multiple attempts")
                return False
    return False


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
