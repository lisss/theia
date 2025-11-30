from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://theia:theia@db:5432/theia'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Models
class Metric(db.Model):
    __tablename__ = 'metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    tags = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    source = db.Column(db.String(255), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'tags': self.tags or {},
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }


# API Routes
@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get metrics with optional filtering"""
    name = request.args.get('name')
    source = request.args.get('source')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    limit = request.args.get('limit', type=int, default=1000)
    
    query = Metric.query
    
    if name:
        query = query.filter(Metric.name == name)
    if source:
        query = query.filter(Metric.source == source)
    if start_time:
        query = query.filter(Metric.timestamp >= datetime.fromisoformat(start_time))
    if end_time:
        query = query.filter(Metric.timestamp <= datetime.fromisoformat(end_time))
    
    query = query.order_by(Metric.timestamp.desc()).limit(limit)
    metrics = query.all()
    
    return jsonify([metric.to_dict() for metric in metrics])


@app.route('/api/metrics/aggregate', methods=['GET'])
def get_aggregated_metrics():
    """Get aggregated metrics grouped by name and time window"""
    from sqlalchemy import func, text
    
    name = request.args.get('name')
    window = request.args.get('window', '1h')  # 1m, 5m, 1h, 1d
    
    # Map window to PostgreSQL date_trunc format
    # For 5m, we'll use a custom expression to round to 5-minute intervals
    if window == '5m':
        # Group by 5-minute intervals: truncate to hour, then add rounded minutes
        time_bucket_expr = func.date_trunc('hour', Metric.timestamp) + \
            text("INTERVAL '1 minute' * (FLOOR(EXTRACT(minute FROM metrics.timestamp)::int / 5) * 5)")
    else:
        window_map = {
            '1m': 'minute',
            '1h': 'hour',
            '1d': 'day'
        }
        trunc_unit = window_map.get(window, 'hour')
        time_bucket_expr = func.date_trunc(trunc_unit, Metric.timestamp)
    
    query = db.session.query(
        Metric.name,
        time_bucket_expr.label('time_bucket'),
        func.avg(Metric.value).label('avg_value'),
        func.count(Metric.id).label('count')
    )
    
    if name:
        query = query.filter(Metric.name == name)
    
    query = query.group_by(Metric.name, 'time_bucket').order_by('time_bucket')
    results = query.all()
    
    return jsonify([{
        'name': r.name,
        'time_bucket': r.time_bucket.isoformat() if r.time_bucket else None,
        'avg_value': float(r.avg_value),
        'count': r.count
    } for r in results])


@app.route('/api/metrics/names', methods=['GET'])
def get_metric_names():
    """Get list of all unique metric names"""
    names = db.session.query(Metric.name).distinct().all()
    return jsonify([name[0] for name in names])


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


def init_db():
    """Initialize database tables"""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with app.app_context():
                db.create_all()
            print("Database initialized successfully!")
            return True
        except Exception as e:
            retry_count += 1
            print(f"Database connection failed (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(2)
            else:
                print("Failed to initialize database after multiple attempts")
                return False
    return False

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

