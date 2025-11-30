# Accessing PostgreSQL Database

## Connection Details

- **Host**: localhost (or 127.0.0.1)
- **Port**: 5432
- **Database**: theia
- **Username**: theia
- **Password**: theia

## CLI Access

### Using Docker Exec (Recommended)

Access the database directly from the container:

```bash
docker-compose exec db psql -U theia -d theia
```

Or use the postgres superuser:

```bash
docker-compose exec db psql -U postgres
```

### Using Local psql Client

If you have PostgreSQL client installed locally:

```bash
psql -h localhost -p 5432 -U theia -d theia
```

When prompted, enter password: `theia`

### Common psql Commands

Once connected, you can run SQL commands:

```sql
-- List all tables
\dt

-- Describe a table structure
\d metrics

-- View all metrics
SELECT * FROM metrics;

-- Count metrics
SELECT COUNT(*) FROM metrics;

-- View recent metrics
SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 10;

-- Exit psql
\q
```

## UI Database Browsers

### Option 1: pgAdmin (Web-based)

Add pgAdmin to docker-compose.yml:

```yaml
  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@theia.local
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - db
```

Then access at http://localhost:5050

### Option 2: DBeaver (Desktop App)

1. Download from https://dbeaver.io/
2. Create new connection → PostgreSQL
3. Enter connection details:
   - Host: localhost
   - Port: 5432
   - Database: theia
   - Username: theia
   - Password: theia

### Option 3: TablePlus (macOS/Windows)

1. Download from https://tableplus.com/
2. Create new connection → PostgreSQL
3. Enter connection details (same as above)

### Option 4: Postico (macOS only)

1. Download from https://eggerapps.at/postico/
2. Create new favorite with connection details

### Option 5: VS Code Extensions

- **PostgreSQL** by Chris Kolkman
- **SQLTools** with PostgreSQL driver

## Quick Database Queries

### View all metrics
```sql
SELECT * FROM metrics ORDER BY timestamp DESC;
```

### Count metrics by name
```sql
SELECT name, COUNT(*) as count 
FROM metrics 
GROUP BY name 
ORDER BY count DESC;
```

### View metrics in last hour
```sql
SELECT * FROM metrics 
WHERE timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

### Average value by metric name
```sql
SELECT name, AVG(value) as avg_value, COUNT(*) as count
FROM metrics
GROUP BY name;
```

