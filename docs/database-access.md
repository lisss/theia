# Accessing InfluxDB Database

## Connection Details

- **URL**: http://localhost:8086
- **Username**: theia
- **Password**: theia123456
- **Organization**: theia
- **Bucket**: theia
- **Token**: theia-admin-token-123456

## CLI Access

### Using Docker Exec

Access InfluxDB CLI directly from the container:

```bash
docker-compose exec influxdb influx
```

Or use the InfluxDB shell:

```bash
docker-compose exec influxdb influx shell
```

### Common InfluxDB Queries

Once connected, you can run Flux queries:

```flux
# List all buckets
buckets()

# Query metrics from the last hour
from(bucket: "theia")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")

# Count metrics by name
from(bucket: "theia")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> group(columns: ["name"])
  |> count()

# Get average values by metric name
from(bucket: "theia")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> group(columns: ["name"])
  |> mean(column: "_value")
```

## UI Database Browsers

### Option 1: InfluxDB UI (Built-in)

Access the InfluxDB web UI directly:

1. Open http://localhost:8086 in your browser
2. Login with:
   - Username: `theia`
   - Password: `theia123456`
3. Navigate to the Data Explorer to run queries
4. Use the Script Editor for advanced Flux queries

### Option 2: Chronograf (InfluxDB Dashboard)

Chronograf is the official InfluxDB dashboard tool. You can add it to docker-compose:

```yaml
  chronograf:
    image: chronograf:latest
    ports:
      - "8888:8888"
    environment:
      INFLUXDB_URL: http://influxdb:8086
    depends_on:
      - influxdb
```

Then access at http://localhost:8888

### Option 3: Grafana

Grafana has excellent InfluxDB support:

1. Download from https://grafana.com/
2. Add InfluxDB as a data source:
   - Type: InfluxDB
   - URL: http://localhost:8086
   - Organization: theia
   - Token: theia-admin-token
   - Bucket: theia

### Option 4: VS Code Extensions

- **InfluxDB** extension for VS Code
- **Flux** language support

## Quick Database Queries

### View all metrics from last hour
```flux
from(bucket: "theia")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> limit(n: 100)
```

### Count metrics by name
```flux
from(bucket: "theia")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> group(columns: ["name"])
  |> count()
```

### Average value by metric name
```flux
from(bucket: "theia")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> group(columns: ["name"])
  |> mean(column: "_value")
```

### Filter by specific metric name
```flux
from(bucket: "theia")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "metrics")
  |> filter(fn: (r) => r["_field"] == "value")
  |> filter(fn: (r) => r["name"] == "button_clicks")
```

## InfluxDB Benefits for Time-Series Data

- **Optimized for time-series**: Much faster queries and writes than SQL databases
- **Automatic data retention**: Built-in retention policies
- **Efficient compression**: Better storage efficiency for time-series data
- **Native aggregation**: Built-in functions for time-based aggregations
- **Tag-based indexing**: Fast filtering by tags (metadata)
- **Downsampling**: Automatic data downsampling for long-term storage
