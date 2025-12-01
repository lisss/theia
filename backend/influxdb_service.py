from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
import os
from datetime import datetime

class InfluxDB:
    def __init__(self):
        self.url = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
        self.token = os.getenv('INFLUXDB_TOKEN', 'theia-admin-token-123456')
        self.org = os.getenv('INFLUXDB_ORG', 'theia')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'theia')
        
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
    
    def write_metric(self, name, value, tags=None, timestamp=None, source=None):
        """Write a single metric to InfluxDB"""
        point = Point("metrics")
        point.field("value", float(value))
        point.tag("name", name)
        
        if tags:
            for key, val in tags.items():
                point.tag(key, str(val))
        
        if source:
            point.tag("source", source)
        
        if timestamp:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            point.time(timestamp)
        else:
            point.time(datetime.utcnow())
        
        try:
            self.write_api.write(bucket=self.bucket, record=point)
            return True
        except InfluxDBError as e:
            print(f"Error writing to InfluxDB: {e}")
            return False
    
    def query_metrics(self, name=None, source=None, start_time=None, end_time=None, limit=1000):
        """Query metrics from InfluxDB"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time or "-24h"}, stop: {end_time or "now()"})
          |> filter(fn: (r) => r["_measurement"] == "metrics")
          |> filter(fn: (r) => r["_field"] == "value")
        '''
        
        if name:
            query += f'  |> filter(fn: (r) => r["name"] == "{name}")\n'
        if source:
            query += f'  |> filter(fn: (r) => r["source"] == "{source}")\n'
        
        query += f'  |> limit(n: {limit})\n'
        query += '  |> sort(columns: ["_time"], desc: true)'
        
        try:
            result = self.query_api.query(org=self.org, query=query)
            metrics = []
            for table in result:
                for record in table.records:
                    # Use record.values - tags are preserved in the dict
                    values = record.values if hasattr(record, 'values') else {}
                    
                    # Extract metric data - tags like 'name', 'source', 'button', 'page' are in values
                    # But due to duplicate column names warning, we need to be careful
                    metric_name = values.get('name', '')
                    # If name not found, try to get from row list (index 8 based on earlier test)
                    if not metric_name and hasattr(record, 'row') and isinstance(record.row, list) and len(record.row) > 8:
                        metric_name = record.row[8] if isinstance(record.row[8], str) else ''
                    
                    metric_value = record.get_value()
                    metric_time = record.get_time()
                    metric_source = values.get('source', '')
                    
                    # Get tags - extract from values, excluding system fields
                    tags = {}
                    if isinstance(values, dict):
                        # Get all non-system fields as tags
                        for k, v in values.items():
                            if k not in ['_measurement', '_field', '_time', '_value', '_start', '_stop', 
                                        'result', 'table', ''] and not k.startswith('_'):
                                tags[k] = v
                    
                    if metric_time and metric_value is not None:
                        metric = {
                            'name': metric_name,
                            'value': float(metric_value),
                            'timestamp': metric_time.isoformat(),
                            'tags': tags,
                            'source': metric_source
                        }
                        metrics.append(metric)
            return metrics
        except Exception as e:
            print(f"Error querying InfluxDB: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def query_aggregated_metrics(self, name=None, window='1h', aggregate_fn='mean'):
        """Query aggregated metrics grouped by time window"""
        from collections import defaultdict
        from datetime import timedelta
        
        # Get raw metrics first - use longer time range for aggregation
        raw_metrics = self.query_metrics(name=name, start_time="-24h", limit=10000)
        
        if not raw_metrics:
            return []
        
        # Parse window to timedelta
        window_map = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '1h': timedelta(hours=1),
            '1d': timedelta(days=1)
        }
        window_delta = window_map.get(window, timedelta(hours=1))
        
        # Group by time bucket and metric name
        buckets = defaultdict(lambda: {'values': [], 'name': name or 'unknown'})
        
        for metric in raw_metrics:
            try:
                timestamp = datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00'))
                # Round down to window boundary
                bucket_time = timestamp.replace(
                    minute=(timestamp.minute // window_delta.seconds * 60) % 60 if window_delta.seconds < 3600 else 0,
                    second=0,
                    microsecond=0
                )
                if window_delta >= timedelta(hours=1):
                    bucket_time = bucket_time.replace(minute=0)
                if window_delta >= timedelta(days=1):
                    bucket_time = bucket_time.replace(hour=0)
                
                metric_name = metric.get('name', name or 'unknown')
                bucket_key = (bucket_time.isoformat(), metric_name)
                buckets[bucket_key]['values'].append(metric['value'])
                buckets[bucket_key]['name'] = metric_name
            except Exception as e:
                continue
        
        # Calculate aggregation based on function
        aggregated = []
        for (time_bucket, metric_name), data in buckets.items():
            if data['values']:
                values = data['values']
                aggregated_value = 0.0
                
                if aggregate_fn == 'mean' or aggregate_fn == 'avg':
                    aggregated_value = sum(values) / len(values)
                elif aggregate_fn == 'sum':
                    aggregated_value = sum(values)
                elif aggregate_fn == 'max':
                    aggregated_value = max(values)
                elif aggregate_fn == 'min':
                    aggregated_value = min(values)
                elif aggregate_fn == 'count':
                    aggregated_value = len(values)
                elif aggregate_fn == 'last':
                    aggregated_value = values[-1] if values else 0.0
                else:
                    # Default to mean
                    aggregated_value = sum(values) / len(values)
                
                aggregated.append({
                    'name': data['name'],
                    'time_bucket': time_bucket,
                    'avg_value': aggregated_value,  # Keep field name for compatibility
                    'count': len(values)
                })
        
        # Sort by time
        aggregated.sort(key=lambda x: x['time_bucket'])
        return aggregated
    
    def get_metric_names(self):
        """Get list of all unique metric names"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: -30d)
          |> filter(fn: (r) => r["_measurement"] == "metrics")
          |> filter(fn: (r) => r["_field"] == "value")
          |> keep(columns: ["name"])
          |> distinct(column: "name")
        '''
        
        try:
            result = self.query_api.query(org=self.org, query=query)
            names = []
            for table in result:
                for record in table.records:
                    name = record.values.get('name')
                    if name and name not in names:
                        names.append(name)
            return sorted(names)
        except Exception as e:
            print(f"Error getting metric names: {e}")
            return []
    
    def close(self):
        """Close the InfluxDB client"""
        self.client.close()

