# YorkU Multi-DB FastAPI

A production-ready FastAPI application that connects to Oracle, MySQL, MS SQL, and PostgreSQL with environment-based configuration, API key authentication, and advanced query capabilities.

## Features
- 🔌 **Multi-Database Support**: Oracle, MySQL, PostgreSQL, MS SQL Server
- 🔐 **API Key Authentication**: Secure endpoints with header-based auth
- 📊 **Two Query Modes**:
  - `getRecord`: Single record retrieval with exact match validation
  - `sqlExec`: Custom SQL with pagination (up to 300 records/page)
- 🔄 **Universal Parameter Syntax**: Use `:param` for all databases (auto-converts)
- 📄 **Full Pagination**: Includes total records, total pages, and navigation
- 🐳 **Docker Ready**: Complete containerization with Oracle Instant Client
- 📝 **Interactive Docs**: Swagger UI and ReDoc (DEV mode)
- 🏥 **Health Checks**: Built-in monitoring endpoints

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Quick start script
./docker-start.sh

# Or manually
docker compose -f docker compose.prod.yml up -d

# View logs
docker compose logs -f

# Or use Makefile
make up
make logs
```

### Option 2: Local Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Oracle Instant Client (for Oracle support)
./install_oracle_client.sh

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start server
python run_server.py
```

API will be available at: http://localhost:8082

## Docker Deployment

### Quick Commands

```bash
# Production
make build          # Build image
make up             # Start container
make logs           # View logs
make down           # Stop container

# Development (with hot-reload)
make dev-build      # Build dev image
make dev-up         # Start dev container
make dev-logs       # View dev logs
```

### Building Multi-Architecture Images for Docker Hub

Build and push to Docker Hub for multiple platforms (amd64, arm64, arm/v7):

```bash
# 1. Edit build.sh and set your Docker Hub username
DOCKER_USERNAME="your-username"

# 2. Run the build script
./build.sh
```

This creates multi-architecture images that work on:
- ✅ x86-64 servers (Intel/AMD)
- ✅ ARM servers (AWS Graviton, Apple M1/M2)
- ✅ Raspberry Pi and ARM devices

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for complete documentation on:
- Multi-platform builds (amd64, arm64, arm/v7)
- Publishing to Docker Hub
- Version tagging strategies
- CI/CD integration

### What's Included in Docker Image

✅ Python 3.12  
✅ Oracle Instant Client 21.15 (thick mode)  
✅ MS SQL ODBC Driver 17  
✅ PostgreSQL client libraries  
✅ MySQL client libraries  
✅ All Python dependencies  
✅ Health checks  
✅ Non-root user execution  

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for complete documentation.

## Configuration

### Environment File

The `.env` file is mapped into the Docker container (or used directly in local mode):

```bash
# Application
APP_MODE=PROD
API_KEY=your_secure_api_key

# Oracle Instant Client (auto-configured in Docker)
ORACLE_CLIENT_LIB=/opt/oracle/instantclient_21_15

# Database Configurations (JSON format for multiple servers)
ORACLE_CONFIGS={"server1":{...},"server2":{...}}
MYSQL_CONFIGS={"server1":{...}}
# ... see .env.example for complete list
```

### Multiple Servers

Configure multiple database servers per type:

```bash
MYSQL_CONFIGS={"primary":{"host":"db1","port":3306,"db":"mydb","user":"user1","password":"pass1"},"analytics":{"host":"db2","port":3306,"db":"analytics","user":"user2","password":"pass2"}}
```

## API Endpoints

### Health Check
```bash
GET /health
```

### List Available Connections
```bash
GET /connections
```

Discover all configured database connections:
```json
{
  "status": "success",
  "summary": {
    "total_connections": 5,
    "by_type": {"oracle": 2, "mysql": 2, "postgres": 1, "mssql": 0}
  },
  "connections": {
    "oracle": {"yustart": {...}, "eclass": {...}},
    "mysql": {"Early Alerts": {...}, "default": {...}},
    ...
  }
}
```

### Get Single Record
```bash
POST /getRecord
{
  "dbtype": "oracle",
  "server": "yustart",
  "table": "users",
  "parameters": {"user_id": 12345},
  "fields": "user_id,username,email"
}
```

### Execute Custom SQL
```bash
POST /sqlExec
{
  "dbtype": "mysql",
  "sql": "SELECT * FROM users WHERE status = :status ORDER BY id",
  "parameters": {"status": "active"},
  "page": 1,
  "page_size": 100
}
```

Returns:
```json
{
  "status": "success",
  "pagination": {
    "page": 1,
    "page_size": 100,
    "record_count": 100,
    "total_records": 1523,
    "total_pages": 16,
    "has_more": true,
    "next_page": 2
  },
  "records": [...]
}
```

## Documentation

- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - Complete Docker guide
- **[CONNECTIONS_API.md](CONNECTIONS_API.md)** - Connections endpoint docs
- **[GET_RECORD_API.md](GET_RECORD_API.md)** - getRecord endpoint docs
- **[SQL_EXEC_API.md](SQL_EXEC_API.md)** - sqlExec endpoint docs
- **[ORACLE_SETUP.md](ORACLE_SETUP.md)** - Oracle configuration guide
- **[DEBUGGING.md](DEBUGGING.md)** - Troubleshooting guide

## API Authentication

Send `X-API-KEY` header with requests:

```bash
curl -X POST http://localhost:8082/sqlExec \
  -H 'X-API-KEY: your_api_key' \
  -H 'Content-Type: application/json' \
  -d '{...}'
```

Multiple API keys supported via `API_KEYS` in `.env`.

## Development

### Local Development with Hot-Reload

```bash
# Using Docker (recommended)
make dev-up

# Or locally
python run_server.py
```

Interactive API docs available at:
- Swagger UI: http://localhost:8082/docs
- ReDoc: http://localhost:8082/redoc

### Running Tests

```bash
# In Docker
make test

# Or locally
pytest
```

## Production Deployment

### Using Docker Compose

```bash
# Production mode
docker compose -f docker compose.prod.yml up -d

# Behind reverse proxy (Nginx/Traefik)
# See DOCKER_DEPLOYMENT.md for configuration
```

### Using Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker compose.prod.yml yorku-api
docker service scale yorku-api_api=3
```

### Resource Limits

Edit `docker compose.prod.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

## Troubleshooting

### Docker Issues

```bash
# View logs
docker compose logs -f api

# Check health
curl http://localhost:8082/health

# Rebuild from scratch
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Oracle Connection Issues

```bash
# Verify Oracle Instant Client
docker compose exec api ls -la /opt/oracle/instantclient_21_15

# Check thick mode
docker compose logs api | grep -i oracle
```

See [DEBUGGING.md](DEBUGGING.md) for comprehensive troubleshooting.

## Security Notes

- ✅ Container runs as non-root user
- ✅ `.env` file mounted read-only
- ✅ Parameterized queries prevent SQL injection
- ✅ API key authentication on all endpoints
- ✅ Minimal Docker image (slim base)
- ✅ No sensitive data in Docker image

## License

[Add your license here]

## Support

- Health endpoint: http://localhost:8082/health
- API docs (DEV): http://localhost:8082/docs
- Documentation: See `*.md` files in project root
