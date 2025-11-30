from flask import Flask, request, jsonify
from flask_cors import CORS
from celery import Celery
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Celery client to send tasks to worker
celery_app = Celery(
    'theia_agent',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@app.route('/metrics', methods=['POST'])
def receive_metric():
    """Receive metrics from clients and queue them"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data or 'value' not in data:
            return jsonify({'error': 'Missing required fields: name and value'}), 400
        
        # Prepare metric data
        metric_data = {
            'name': data['name'],
            'value': data['value'],
            'tags': data.get('tags', {}),
            'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
            'source': data.get('source', request.remote_addr)
        }
        
        # Queue the metric for processing
        celery_app.send_task('process_metric', args=[metric_data])
        
        return jsonify({'status': 'queued', 'message': 'Metric queued for processing'}), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/metrics/batch', methods=['POST'])
def receive_metrics_batch():
    """Receive multiple metrics in a batch"""
    try:
        data = request.get_json()
        
        if not data or 'metrics' not in data:
            return jsonify({'error': 'Missing required field: metrics'}), 400
        
        metrics = data['metrics']
        queued_count = 0
        
        for metric in metrics:
            if 'name' in metric and 'value' in metric:
                metric_data = {
                    'name': metric['name'],
                    'value': metric['value'],
                    'tags': metric.get('tags', {}),
                    'timestamp': metric.get('timestamp', datetime.utcnow().isoformat()),
                    'source': metric.get('source', request.remote_addr)
                }
                celery_app.send_task('process_metric', args=[metric_data])
                queued_count += 1
        
        return jsonify({
            'status': 'queued',
            'queued_count': queued_count,
            'total_count': len(metrics)
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

