# YorkU Multi-DB FastAPI

A starter FastAPI application that connects to Oracle, MySQL, MS SQL, and PostgreSQL with environment-based configuration, simple API key auth, and mixed queries.

## Features
- Separate connectors and query functions for Oracle, MySQL, MS SQL (ODBC), Postgres
- .env-driven configuration per DB system
- DEV/PROD mode controls docs availability
- API key enforcement via `X-API-KEY` header; supports multiple keys
- Demo endpoints, including a mixed multi-DB query

## Setup
1. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and edit values:

```bash
cp .env.example .env
# edit .env with your credentials
```

3. Start the server (always on port 8082):

```bash
python run_server.py
```

- Docs (DEV only): http://localhost:8082/docs
- Health: http://localhost:8082/health

## API Key
Send `X-API-KEY` header with a valid key from `.env`. If `API_KEYS` (JSON array) is present, it overrides `API_KEY`.

## Mixed Query Example
`GET /mixed/sample` performs basic queries against MySQL and Postgres and returns combined data.

## Notes
- Ensure required DB client libraries and drivers are installed:
  - Oracle Instant Client for `cx_Oracle`
  - ODBC driver for SQL Server (e.g., `msodbcsql17`) for `pyodbc`
- Replace sample queries with your own as needed.
