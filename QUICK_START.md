# Quick Start Guide

## 1. Query button_clicks in InfluxDB UI

### Access InfluxDB UI:
1. Open http://localhost:8086
2. Login:
   - Username: `theia`
   - Password: `theia123456`

### Query button_clicks:
1. Click **Data Explorer** in left sidebar
2. Click **Script Editor**
3. Paste this query:

```flux
from(bucket: "theia")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "button_clicks")
  |> limit(n: 100)
```

4. Click **Submit** to see results
5. Click **Visualize** to see as a chart

### Aggregated query (by time window):
```flux
from(bucket: "theia")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "button_clicks")
  |> group(columns: ["name"])
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> sort(columns: ["_time"])
```

## 2. View Metrics in Theia Frontend

### Access Frontend:
- URL: http://localhost:3000

### Steps:
1. The frontend will automatically load available metric names
2. Check the boxes next to metrics you want to view (e.g., `button_clicks`, `page_views`)
3. Graphs will appear showing the aggregated metrics over time
4. Data refreshes every 5 seconds automatically

### If no data shows:
1. Check browser console (F12) for errors
2. Verify backend is running: `docker-compose ps backend`
3. Test API directly: `curl http://localhost:5001/api/metrics/names`
4. Check if metrics exist: `curl http://localhost:5001/api/metrics/aggregate?name=button_clicks&window=5m`

## Sample Data

The database contains 250 sample metrics:
- `button_clicks` (50 metrics) - Values: 200-1500
- `api_requests` (40 metrics) - Response times
- `page_views` (60 metrics) - Values: 200-1500
- `errors` (15 metrics)
- `cpu_usage` (30 metrics)
- `memory_usage` (30 metrics)
- `db_query_time` (25 metrics)

## Troubleshooting

### No metrics in frontend:
- Refresh the page
- Check browser console for API errors
- Verify backend API: `curl http://localhost:5001/api/metrics/names`

### InfluxDB UI not accessible:
- Check if InfluxDB is running: `docker-compose ps influxdb`
- Check logs: `docker-compose logs influxdb`

### Need more data:
```bash
./scripts/populate_data.sh
```

