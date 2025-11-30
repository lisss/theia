# Theia - Simple Observability Tool

A lightweight observability tool similar to Datadog, designed to collect, store, and visualize metrics from your applications.

## Architecture

Theia consists of several components:

1. **Agent** - Receives metrics from clients and queues them (port 8000)
2. **Message Queue** - Redis-based queue for async processing
3. **Worker** - Celery worker that processes queued metrics and stores them in the database
4. **Backend API** - Flask API that serves metrics data (port 5001)
5. **Frontend** - React + TypeScript dashboard for visualizing metrics (port 3000)
6. **Database** - PostgreSQL for storing metrics

## Features

- **Easy Configuration**: Send any metric or event from your applications
- **Async Processing**: Metrics are queued, so clients don't wait for database writes
- **Real-time Visualization**: View metrics as graphs in the web dashboard
- **Flexible Metrics**: Support for custom metric names, values, tags, and sources

## Quick Start with Docker

### Building Images (with Layer Caching)

The Dockerfiles are optimized for layer caching. Dependencies are installed before application code, so code changes don't require reinstalling dependencies.

**Build all images:**
```bash
docker-compose build
```

**Build specific service:**
```bash
docker-compose build backend
docker-compose build frontend
docker-compose build agent
```

**Build with no cache (fresh build):**
```bash
docker-compose build --no-cache
```

### Running Services

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to be ready** (about 30 seconds)

3. **Access the dashboard:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001
   - Agent: http://localhost:8000

**Note:** Docker Compose will automatically build images if they don't exist, but for better control, build images first using `docker-compose build`.

### Troubleshooting Docker Issues

If you encounter network errors when pulling Docker images (e.g., "EOF" or "TLS handshake timeout"):

1. **Retry the command** - Docker Hub connectivity can be intermittent:
   ```bash
   docker-compose up -d
   ```

2. **Manually pull images** if automatic pull fails:
   ```bash
   docker pull redis:7-alpine
   docker pull postgres:15-alpine
   ```

3. **Check your network connection** - Ensure you can access Docker Hub:
   ```bash
   curl -I https://registry-1.docker.io
   ```

4. **Check Docker daemon** - Ensure Docker is running:
   ```bash
   docker info
   ```

5. **Use cached images** - If images are already cached locally, Docker Compose will use them automatically.

## Sending Metrics

### Single Metric

Send a POST request to the agent:

```bash
curl -X POST http://localhost:8000/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "name": "button_clicks",
    "value": 1,
    "tags": {"button": "submit", "page": "home"},
    "source": "web-app"
  }'
```

### Batch Metrics

Send multiple metrics at once:

```bash
curl -X POST http://localhost:8000/metrics/batch \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": [
      {"name": "button_clicks", "value": 1, "tags": {"button": "submit"}},
      {"name": "api_requests", "value": 1, "tags": {"endpoint": "/api/users"}},
      {"name": "page_views", "value": 1, "tags": {"page": "home"}}
    ]
  }'
```

### Example: Simulating Button Clicks

```bash
# Simulate multiple button clicks
for i in {1..10}; do
  curl -X POST http://localhost:8000/metrics \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"button_clicks\", \"value\": 1, \"tags\": {\"button\": \"submit\"}}"
  sleep 1
done
```

## API Endpoints

### Agent Endpoints (Port 8000)

- `POST /metrics` - Send a single metric
- `POST /metrics/batch` - Send multiple metrics
- `GET /health` - Health check

### Backend API Endpoints (Port 5001)

- `GET /api/metrics` - Get metrics (supports query params: name, source, start_time, end_time, limit)
- `GET /api/metrics/aggregate` - Get aggregated metrics (supports query params: name, window)
- `GET /api/metrics/names` - Get list of all metric names
- `GET /health` - Health check

## Development Setup

### Backend

1. Create virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export DATABASE_URL=postgresql://theia:theia@localhost:5432/theia
   export REDIS_URL=redis://localhost:6379/0
   ```

4. Run the backend:
   ```bash
   python app.py
   ```

5. Run the worker (in another terminal):
   ```bash
   celery -A worker.celery_app worker --loglevel=info
   ```

### Agent

1. Create virtual environment:
   ```bash
   cd agent
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export REDIS_URL=redis://localhost:6379/0
   ```

4. Run the agent:
   ```bash
   python app.py
   ```

### Frontend

1. Install dependencies:
   ```bash
   cd frontend
   yarn install
   ```

2. Set environment variable (optional):
   ```bash
   export REACT_APP_API_URL=http://localhost:5001
   ```

3. Run the frontend:
   ```bash
   yarn start
   ```

## Configuration

### Metric Format

Each metric should have:
- `name` (required): Name of the metric (e.g., "button_clicks", "api_requests")
- `value` (required): Numeric value of the metric
- `tags` (optional): Key-value pairs for additional context
- `timestamp` (optional): ISO format timestamp (defaults to current time)
- `source` (optional): Source identifier (defaults to client IP)

### Aggregation Windows

The frontend uses time windows for aggregation:
- `1m` - 1 minute
- `5m` - 5 minutes
- `1h` - 1 hour
- `1d` - 1 day

## Docker Services

- **db**: PostgreSQL database
- **redis**: Redis message queue
- **backend**: Flask API server
- **worker**: Celery worker for processing metrics
- **agent**: Metric collection agent
- **frontend**: React development server

## Database Access

### Quick CLI Access

```bash
docker-compose exec db psql -U theia -d theia
```

### Connection Details for UI Tools

- **Host**: localhost
- **Port**: 5432
- **Database**: theia
- **Username**: theia
- **Password**: theia

**Popular UI Tools:**
- **DBeaver**: https://dbeaver.io/ (Free, cross-platform)
- **TablePlus**: https://tableplus.com/ (macOS/Windows)
- **pgAdmin**: Web-based (can be added to docker-compose)

For detailed database access instructions, see [docs/database-access.md](docs/database-access.md)

### Populate Sample Data

To populate the database with sample metrics for testing:

```bash
./scripts/populate_data.sh
```

Or manually:

```bash
docker-compose exec backend python /scripts/populate_sample_data.py
```

**Note:** The script is located in the `scripts/` directory and is mounted in the container at `/scripts`.

This will create 250 sample metrics including:
- Button clicks
- API requests
- Page views
- Errors
- CPU/Memory usage
- Database query times

The metrics are spread over the last 2 hours, so you'll see them appear in the frontend dashboard graphs.

## Stopping Services

```bash
docker-compose down
```

To remove volumes (database data):
```bash
docker-compose down -v
```

## Docker Build Optimization

The Dockerfiles are optimized for efficient layer caching:

### Layer Caching Strategy

1. **System dependencies** are installed first (rarely change)
2. **Package files** (requirements.txt, package.json) are copied next
3. **Dependencies are installed** before copying application code
4. **Application code** is copied last (changes most frequently)

This means:
- When you change only code, dependency layers remain cached
- When you change dependencies, only dependency layers rebuild
- System dependencies are cached across all builds

### Build Performance Tips

1. **Build images separately** for better control:
   ```bash
   ./build.sh
   # or
   docker-compose build
   ```

2. **Use build cache** - Docker automatically uses cached layers when possible

3. **Worker service** shares the backend image, so it doesn't need a separate build

4. **First build** will be slower (no cache), subsequent builds will be faster

5. **Force rebuild** when needed:
   ```bash
   docker-compose build --no-cache
   ```

## License

MIT
