# Software Architecture

## Overview
The Python Multi-DB FastAPI project provides a lightweight HTTP API that proxies queries for Oracle, MySQL, PostgreSQL, and MSSQL databases. FastAPI exposes standardized endpoints with API-key protection and database-agnostic helpers so different teams can reuse the same entry point while targeting different database engines.

## Core Components
1. **FastAPI app (`app/main.py`)**
   - Defines endpoints such as `/oracle/sample`, `/get-record`, `/sql-exec`, `/insert-record`, `/update-record`, and `/delete-record`.
   - Each route depends on `auth.verify_api_key` to enforce the OpenAPI `X-API-KEY` security scheme.
   - Routes invoke helper classes from the `db_*` modules to manage engine-specific queries.

2. **Configuration (`app/config.py`)**
   - Loads all environment-driven settings (`.env`), including connection definitions per database type and API keys.
   - Exposes typed constants such as `API_KEYS`, `MYSQL_SERVERS`, `ORACLE_SERVERS`, etc.

3. **Authentication (`app/auth.py`)**
   - Registers a reusable `APIKeyHeader` dependency used across endpoints.
   - Performs simple lookups against `API_KEYS` and raises HTTP 401 if invalid.
   - Ensures OpenAPI documentation shows the single `Authorize` control for `X-API-KEY`.

4. **Database clients (`app/db_mysql.py`, `app/db_postgres.py`, `app/db_mssql.py`, `app/db_oracle.py`)**
   - Each client takes a connection definition (host/service/DSN) and optional pool/cursor helpers.
   - Shared helpers (e.g., `get_record`, `sql_exec`) orchestrate parameter binding to protect against injection.
   - Oracle client supports DSN overrides to reuse existing TNS descriptor strings when needed.

5. **Helper utilities**
   - Pagination logic and parameter parsing live alongside the main route implementations so they can remain database-agnostic while still tailoring to each engine’s syntax (e.g., limit/offset variations).

## Data Flow
1. Client sends request to FastAPI endpoint with `X-API-KEY` header and body parameters.
2. Authentication dependency validates the key and injects a success flag before route logic runs.
3. Route selects the appropriate database helper using the `dbtype` and `server` inputs.
4. Helper builds SQL (SELECT/INSERT/UPDATE/DELETE) and binds parameters safely.
5. Results/acknowledgments are returned with pagination metadata when applicable.

## Deployment Considerations
- The project can run in any environment with Python 3.12+, FastAPI, and ORACLE/ODBC clients installed.
- Containerized deployments are supported via the provided `Dockerfile`, `docker-compose.yml`, and `build.sh` that trigger multi-architecture builds and allow external `.env` overrides.
- The OpenAPI schema and auto-generated docs help developers explore available endpoints, parameters, and security requirements.

