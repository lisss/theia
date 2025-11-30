from celery import Celery
from app import app, db, Metric
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Celery configuration
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
    """Process a metric and store it in the database"""
    with app.app_context():
        try:
            metric = Metric(
                name=metric_data['name'],
                value=float(metric_data['value']),
                tags=metric_data.get('tags', {}),
                timestamp=datetime.fromisoformat(metric_data.get('timestamp', datetime.utcnow().isoformat())),
                source=metric_data.get('source')
            )
            db.session.add(metric)
            db.session.commit()
            return {'status': 'success', 'metric_id': metric.id}
        except Exception as e:
            db.session.rollback()
            return {'status': 'error', 'message': str(e)}


if __name__ == '__main__':
    celery_app.start()

