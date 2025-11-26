from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .config import APP_MODE, get_mysql_config, get_pg_config, get_oracle_config, get_mssql_config
from .auth import verify_api_key
from .db_mysql import MySQLDB
from .db_postgres import PostgresDB

app = FastAPI(
    title="YorkU Multi-DB API",
    docs_url="/docs" if APP_MODE == "DEV" else None,
    redoc_url="/redoc" if APP_MODE == "DEV" else None,
    openapi_url="/openapi.json" if APP_MODE == "DEV" else None,
)

# Allow CORS for dev convenience (customize domains as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
async def health():
    return {"status": "ok", "mode": APP_MODE}

@app.get("/mysql/sample")
async def mysql_sample(_: bool = Depends(verify_api_key), server: str | None = Query(None)):
    cfg = get_mysql_config(server)
    db = MySQLDB(cfg)
    try:
        rows = db.query("SELECT 1 as one")
        return {"server": server or "default", "data": rows}
    finally:
        db.close()

@app.get("/postgres/sample")
async def postgres_sample(_: bool = Depends(verify_api_key), server: str | None = Query(None)):
    cfg = get_pg_config(server)
    db = PostgresDB(cfg)
    try:
        rows = db.query("SELECT 1 as one")
        return {"server": server or "default", "data": rows}
    finally:
        db.close()

@app.get("/oracle/sample")
async def oracle_sample(_: bool = Depends(verify_api_key), server: str | None = Query(None)):
    try:
        from .db_oracle import OracleDB
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Oracle driver not available: {e}")
    cfg = get_oracle_config(server)
    db = OracleDB(cfg)
    try:
        rows = db.query("SELECT 1 AS one FROM dual")
        return {"server": server or "default", "data": rows}
    finally:
        db.close()

@app.get("/mssql/sample")
async def mssql_sample(_: bool = Depends(verify_api_key), server: str | None = Query(None)):
    try:
        from .db_mssql import MSSQLDB
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MS SQL ODBC driver not available: {e}")
    cfg = get_mssql_config(server)
    db = MSSQLDB(cfg)
    try:
        rows = db.query("SELECT 1 as one")
        return {"server": server or "default", "data": rows}
    finally:
        db.close()

@app.get("/mixed/sample")
async def mixed_sample(_: bool = Depends(verify_api_key), mysql_server: str | None = Query(None), pg_server: str | None = Query(None)):
    """Demonstrates combining data from multiple DBs, with server selection via query params."""
    mysql = MySQLDB(get_mysql_config(mysql_server))
    pg = PostgresDB(get_pg_config(pg_server))
    try:
        m = mysql.query("SELECT 1 as mysql_one")
        p = pg.query("SELECT 2 as pg_two")
        return {
            "mysql_server": mysql_server or "default",
            "postgres_server": pg_server or "default",
            "mysql": m,
            "postgres": p,
            "sum": (m[0]["mysql_one"] + p[0]["pg_two"]) if m and p else None
        }
    finally:
        mysql.close()
        pg.close()
