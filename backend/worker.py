from celery import Celery
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

from influxdb_service import InfluxDB

influxdb = InfluxDB()

celery_app = Celery(
    'theia_worker',
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


@celery_app.task(name='process_metric')
def process_metric(metric_data):
    """Process a metric and store it in InfluxDB"""
    try:
        success = influxdb.write_metric(
            name=metric_data['name'],
            value=metric_data['value'],
            tags=metric_data.get('tags', {}),
            timestamp=metric_data.get('timestamp'),
            source=metric_data.get('source')
        )
        if success:
            return {'status': 'success'}
        else:
            return {'status': 'error', 'message': 'Failed to write to InfluxDB'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


if __name__ == '__main__':
    celery_app.start()
