# InfluxDB Query Examples

## Querying button_clicks in InfluxDB UI

### Step 1: Access InfluxDB UI
1. Open http://localhost:8086 in your browser
2. Login with:
   - Username: `theia`
   - Password: `theia123456`

### Step 2: Go to Data Explorer
1. Click on **Data Explorer** in the left sidebar
2. Click **Script Editor** to write custom Flux queries

### Step 3: Query button_clicks

**Basic query - all button_clicks:**
```flux
from(bucket: "theia")
  |> range(start: -2h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "button_clicks")
  |> limit(n: 100)
```

**Aggregated by time window (1 minute):**
```flux
from(bucket: "theia")
  |> range(start: -2h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "button_clicks")
  |> group(columns: ["name"])
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> sort(columns: ["_time"])
```

**Count button_clicks by button type:**
```flux
from(bucket: "theia")
  |> range(start: -2h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "button_clicks")
  |> group(columns: ["button"])
  |> count()
```

**Sum of button_clicks over time:**
```flux
from(bucket: "theia")
  |> range(start: -2h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "button_clicks")
  |> group(columns: ["name"])
  |> aggregateWindow(every: 5m, fn: sum, createEmpty: false)
```

**Filter by specific button:**
```flux
from(bucket: "theia")
  |> range(start: -2h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "button_clicks")
  |> filter(fn: (r) => r["button"] == "submit")
  |> limit(n: 50)
```

## Other Useful Queries

### Query all metrics:
```flux
from(bucket: "theia")
  |> range(start: -2h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> limit(n: 100)
```

### List all metric names:
```flux
from(bucket: "theia")
  |> range(start: -30d)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> keep(columns: ["name"])
  |> distinct(column: "name")
```

### Average API response time:
```flux
from(bucket: "theia")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "api_requests")
  |> group(columns: ["name"])
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
```

### CPU usage by server:
```flux
from(bucket: "theia")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "cpu_usage")
  |> group(columns: ["server"])
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
```

## Tips

1. **Time Range**: Adjust `start: -2h` to change the time window (e.g., `-1h`, `-24h`, `-7d`)
2. **Aggregation Functions**: Use `mean`, `sum`, `max`, `min`, `count`, `last` in `aggregateWindow`
3. **Grouping**: Use `group(columns: ["name", "tag"])` to group by multiple fields
4. **Visualization**: Click "Submit" then "Visualize" to see charts in the UI

