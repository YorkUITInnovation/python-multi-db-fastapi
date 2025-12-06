# Docker Deployment Guide

## Quick Start

### 1. Prepare Environment File

Copy the example environment file and configure it:

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 2. Build and Run with Docker Compose

```bash
# Build the Docker image
docker compose build

# Start the container
docker compose up -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

The API will be available at `http://localhost:8082`

## Docker Commands

### Build

```bash
# Build the image
docker compose build

# Build without cache (fresh build)
docker compose build --no-cache
```

### Run

```bash
# Start in background (detached mode)
docker compose up -d

# Start in foreground (see logs)
docker compose up

# Start and rebuild if needed
docker compose up -d --build
```

### Manage

```bash
# View running containers
docker compose ps

# View logs
docker compose logs -f api

# Stop containers
docker compose down

# Stop and remove volumes
docker compose down -v

# Restart container
docker compose restart
```

### Execute Commands in Container

```bash
# Open a shell in the running container
docker compose exec api bash

# Run a Python command
docker compose exec api python -c "from app.config import API_KEYS; print(API_KEYS)"

# Check Oracle Instant Client
docker compose exec api ls -la /opt/oracle/instantclient_21_15
```

## Configuration

### Environment Variables

The `.env` file is mapped from your host machine into the container at `/app/.env`. This means:

✅ You can edit `.env` on your host machine  
✅ Changes require container restart: `docker compose restart`  
✅ Sensitive data stays outside the Docker image  

### Port Configuration

The default port is `8082`. To change it:

**Option 1: Edit docker compose.yml**
```yaml
ports:
  - "9000:8082"  # Host port 9000 maps to container port 8082
```

**Option 2: Use environment variable**
```bash
PORT=9000 docker compose up -d
```

### Production vs Development Mode

Set `APP_MODE` in your `.env` file:

```bash
# Development (enables /docs and /redoc)
APP_MODE=DEV

# Production (disables interactive docs)
APP_MODE=PROD
```

## What's Included

### Installed Drivers

The Docker image includes:

✅ **Oracle Instant Client 21.15** (thick mode support)  
✅ **Microsoft ODBC Driver 17 for SQL Server**  
✅ **PostgreSQL client libraries**  
✅ **MySQL client libraries**  
✅ **Python 3.12**  

### Application Features

- Multi-database support (Oracle, MySQL, PostgreSQL, MS SQL)
- API key authentication
- Automatic parameter syntax conversion
- Pagination with total counts
- Health check endpoint at `/health`

## Dockerfile Details

### Base Image

- **Python 3.12 slim**: Minimal Python runtime
- **Debian-based**: Compatible with most database drivers

### Installed Components

1. **System packages**: `wget`, `unzip`, `curl`, `gcc`, `g++`
2. **Database libraries**: `libaio1`, `libpq-dev`, `libmysqlclient-dev`
3. **Oracle Instant Client**: Downloaded and configured automatically
4. **MS SQL ODBC Driver**: Installed from Microsoft repository
5. **Python packages**: From `requirements.txt`

### Security Features

- Runs as non-root user (`appuser`)
- Read-only `.env` mount
- Health checks configured
- Minimal attack surface (slim base image)

## Health Checks

The container includes a health check that:

- Runs every 30 seconds
- Calls the `/health` endpoint
- Marks container unhealthy after 3 failed attempts
- Has a 40-second startup grace period

Check health status:
```bash
docker compose ps
# Look for "healthy" in the STATE column
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs api

# Check if port 8082 is already in use
lsof -i :8082

# Rebuild from scratch
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Can't Connect to Database

```bash
# Verify .env file exists and is readable
ls -la .env

# Check environment variables in container
docker compose exec api printenv | grep -E "(ORACLE|MYSQL|POSTGRES|MSSQL)"

# Test Oracle Instant Client
docker compose exec api bash -c 'echo $ORACLE_CLIENT_LIB && ls -la $ORACLE_CLIENT_LIB'
```

### Oracle Connection Issues

```bash
# Verify Oracle Instant Client installation
docker compose exec api ldconfig -p | grep oracle

# Check thick mode initialization
docker compose logs api | grep -i oracle
```

### Permission Issues

```bash
# Ensure .env is readable
chmod 644 .env

# Check container user
docker compose exec api whoami
# Should output: appuser
```

## Performance Optimization

### Multi-Worker Setup

The default configuration uses 4 workers. Adjust in Dockerfile:

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082", "--workers", "4"]
```

Recommended workers: `(2 x CPU cores) + 1`

### Resource Limits

Add resource limits to `docker compose.yml`:

```yaml
services:
  api:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 512M
```

## Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker compose.yml yorku-api

# Scale service
docker service scale yorku-api_api=3

# View services
docker service ls

# View logs
docker service logs -f yorku-api_api
```

### Using Kubernetes

Convert docker compose to Kubernetes manifests:

```bash
# Install kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.31.2/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv kompose /usr/local/bin/

# Convert
kompose convert

# Deploy
kubectl apply -f .
```

### Behind a Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8082;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Backup and Maintenance

### Backup .env File

```bash
# Create encrypted backup
tar czf - .env | openssl enc -aes-256-cbc -salt -out env-backup-$(date +%Y%m%d).tar.gz.enc

# Restore
openssl enc -aes-256-cbc -d -in env-backup-20241206.tar.gz.enc | tar xz
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

### View Application Logs

```bash
# Real-time logs
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100 api

# Save logs to file
docker compose logs api > app-logs-$(date +%Y%m%d).log
```

## Testing

### Test Endpoints

```bash
# Health check
curl http://localhost:8082/health

# Oracle test (requires valid credentials in .env)
curl -X POST http://localhost:8082/sqlExec \
  -H 'X-API-KEY: your_api_key' \
  -H 'Content-Type: application/json' \
  -d '{
    "dbtype": "oracle",
    "sql": "SELECT 1 as one FROM dual",
    "page": 1,
    "page_size": 10
  }'
```

### Run Tests Inside Container

```bash
# If you have tests
docker compose exec api pytest

# Or run specific test
docker compose exec api python -m pytest tests/test_oracle.py -v
```

## Environment Variables Reference

Required in `.env` file:

```bash
# Application
APP_MODE=PROD
API_KEY=your_secure_api_key

# Oracle Instant Client (pre-configured in Dockerfile)
ORACLE_CLIENT_LIB=/opt/oracle/instantclient_21_15

# Database Configurations
# See .env.example for complete list
```

## Support

- **Documentation**: See `*.md` files in the project root
- **API Docs**: `http://localhost:8082/docs` (DEV mode only)
- **Health Status**: `http://localhost:8082/health`

## Common Issues

### "Cannot connect to Oracle database"
- Verify `ORACLE_CLIENT_LIB=/opt/oracle/instantclient_21_15` in .env
- Check Oracle database credentials
- Ensure network connectivity to Oracle server

### "Port 8082 already in use"
- Change port mapping in `docker compose.yml`
- Or stop other service using port 8082

### "Permission denied on .env"
- Run: `chmod 644 .env`
- Ensure file is readable by all users

### Container keeps restarting
- Check logs: `docker compose logs api`
- Verify .env file is properly formatted
- Check if all required environment variables are set

