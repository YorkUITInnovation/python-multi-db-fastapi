from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from .config import APP_MODE, get_mysql_config, get_pg_config, get_oracle_config, get_mssql_config
from .auth import verify_api_key
from .db_mysql import MySQLDB
from .db_postgres import PostgresDB
import logging

logger = logging.getLogger(__name__)

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

# Pydantic models for getRecord endpoint
class GetRecordRequest(BaseModel):
    dbtype: str = Field(..., description="Database type: oracle, mysql, postgres, or mssql")
    server: Optional[str] = Field(None, description="Server name from config (optional if only one server configured)")
    table: str = Field(..., description="Table name to query")
    parameters: Dict[str, Any] = Field(..., description="WHERE conditions as key-value pairs, e.g., {'user_id': 123, 'status': 'active'}")
    fields: Optional[str] = Field(None, description="Comma-separated field names (default: *)")

    class Config:
        json_schema_extra = {
            "example": {
                "dbtype": "oracle",
                "server": "yustart",
                "table": "users",
                "parameters": {
                    "user_id": 12345
                },
                "fields": "user_id,username,email"
            }
        }

@app.post("/getRecord")
async def get_record(request: GetRecordRequest, _: bool = Depends(verify_api_key)):
    """
    Get a single record from any database.
    Returns an error if multiple records are found or no records exist.

    Parameters:
    - dbtype: Database type (oracle, mysql, postgres, mssql)
    - server: Server name from config (optional if only one configured)
    - table: Table name
    - parameters: WHERE conditions as key-value pairs (e.g., {"user_id": 123, "status": "active"})
    - fields: Comma-separated field names (default: *)
    """

    # Validate dbtype
    dbtype = request.dbtype.lower()
    if dbtype not in ["oracle", "mysql", "postgres", "mssql"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid dbtype '{request.dbtype}'. Must be one of: oracle, mysql, postgres, mssql"
        )

    # Build field list
    fields = request.fields.strip() if request.fields else "*"

    # Build WHERE clause and parameters based on database type
    # Different databases use different parameter placeholders
    where_parts = []
    params = []

    if not request.parameters:
        raise HTTPException(status_code=400, detail="At least one parameter is required")

    # Process parameters as dictionary
    for i, (field_name, value) in enumerate(request.parameters.items(), 1):
        # Use appropriate placeholder based on database type
        if dbtype == "oracle":
            where_parts.append(f"{field_name} = :{i}")
            params.append(value)
        elif dbtype in ["mysql", "postgres"]:
            where_parts.append(f"{field_name} = %s")
            params.append(value)
        elif dbtype == "mssql":
            where_parts.append(f"{field_name} = ?")
            params.append(value)

    where_clause = " AND ".join(where_parts)

    # Build SQL query
    sql = f"SELECT {fields} FROM {request.table} WHERE {where_clause}"

    logger.info(f"getRecord: dbtype={dbtype}, server={request.server}, table={request.table}, sql={sql}")

    # Execute query based on database type
    db = None
    rows = []
    try:
        if dbtype == "oracle":
            from .db_oracle import OracleDB
            cfg = get_oracle_config(request.server)
            db = OracleDB(cfg)
            # Oracle uses tuples for parameters
            rows = db.query(sql, tuple(params))

        elif dbtype == "mysql":
            cfg = get_mysql_config(request.server)
            db = MySQLDB(cfg)
            rows = db.query(sql, tuple(params))

        elif dbtype == "postgres":
            cfg = get_pg_config(request.server)
            db = PostgresDB(cfg)
            rows = db.query(sql, tuple(params))

        elif dbtype == "mssql":
            from .db_mssql import MSSQLDB
            cfg = get_mssql_config(request.server)
            db = MSSQLDB(cfg)
            rows = db.query(sql, tuple(params))

        # Validate result: must be exactly one record
        if len(rows) == 0:
            raise HTTPException(
                status_code=404,
                detail="No record found matching the specified parameters"
            )
        elif len(rows) > 1:
            raise HTTPException(
                status_code=400,
                detail=f"Multiple records found ({len(rows)} records). Expected only one record. Please refine your parameters."
            )

        # Return the single record
        return {
            "status": "success",
            "dbtype": dbtype,
            "server": request.server or "default",
            "table": request.table,
            "record": rows[0]
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"getRecord error: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
    finally:
        if db:
            db.close()

# Pydantic model for sqlExec endpoint
class SqlExecRequest(BaseModel):
    dbtype: str = Field(..., description="Database type: oracle, mysql, postgres, or mssql")
    server: Optional[str] = Field(None, description="Server name from config (optional if only one server configured)")
    sql: str = Field(..., description="SQL query with named parameters (e.g., WHERE firstname = :firstname)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameter values as key-value pairs (e.g., {'firstname': 'patrick'})")
    page: Optional[int] = Field(1, ge=1, description="Page number (default: 1)")
    page_size: Optional[int] = Field(100, ge=1, le=300, description="Records per page (default: 100, max: 300)")

    class Config:
        json_schema_extra = {
            "example": {
                "dbtype": "oracle",
                "server": "yustart",
                "sql": "SELECT * FROM users WHERE firstname = :firstname AND timemodified BETWEEN :starttime AND :endtime",
                "parameters": {
                    "firstname": "patrick",
                    "starttime": "2024-01-01 11:00:00",
                    "endtime": "2024-01-01 13:00:00"
                },
                "page": 1,
                "page_size": 100
            }
        }

@app.post("/sqlExec")
async def sql_exec(request: SqlExecRequest, _: bool = Depends(verify_api_key)):
    """
    Execute a custom SQL query with optional parameters and pagination.

    Parameters:
    - dbtype: Database type (oracle, mysql, postgres, mssql)
    - server: Server name from config (optional if only one configured)
    - sql: SQL query with named parameters matching the database type
    - parameters: Parameter values as key-value pairs
    - page: Page number (default: 1)
    - page_size: Records per page (default: 100, max: 300)

    Parameter Naming Convention:
    - Oracle: Use :parametername (e.g., WHERE id = :user_id)
    - MySQL/PostgreSQL: Use :parametername OR %(parametername)s (auto-converted from :param)
    - MS SQL: Use :parametername (e.g., WHERE id = :user_id)

    Note: For convenience, you can use :parametername syntax for all databases,
    and it will be automatically converted to the correct format for MySQL/PostgreSQL.

    Returns paginated results with metadata.
    """

    # Validate dbtype
    dbtype = request.dbtype.lower()
    if dbtype not in ["oracle", "mysql", "postgres", "mssql"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid dbtype '{request.dbtype}'. Must be one of: oracle, mysql, postgres, mssql"
        )

    # Validate page_size
    page_size = min(request.page_size or 100, 300)
    page = request.page or 1
    offset = (page - 1) * page_size

    # Process SQL and parameters based on database type
    sql = request.sql.strip()
    params = request.parameters or {}

    logger.info(f"sqlExec: dbtype={dbtype}, server={request.server}, page={page}, page_size={page_size}")
    logger.debug(f"SQL: {sql}")
    logger.debug(f"Parameters: {params}")

    # Convert parameter syntax if needed
    # Auto-convert :param to %(param)s for MySQL/PostgreSQL for user convenience
    if dbtype in ["mysql", "postgres"] and params:
        import re
        # Find all :param_name patterns and convert to %(param_name)s
        for param_name in params.keys():
            # Replace :param_name with %(param_name)s
            sql = re.sub(r':' + re.escape(param_name) + r'\b', f'%({param_name})s', sql)

    # Add pagination to SQL query
    # Different databases have different pagination syntax
    if dbtype == "oracle":
        # Oracle uses OFFSET/FETCH (12c+) or ROWNUM
        # We'll use OFFSET/FETCH for simplicity
        paginated_sql = f"{sql} OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
        # Oracle uses named parameters as-is (:param)
        param_values = params
    elif dbtype in ["mysql", "postgres"]:
        # MySQL and PostgreSQL use LIMIT/OFFSET
        paginated_sql = f"{sql} LIMIT {page_size} OFFSET {offset}"
        # MySQL/PostgreSQL use %(param)s syntax
        param_values = params
    elif dbtype == "mssql":
        # MS SQL uses OFFSET/FETCH
        paginated_sql = f"{sql} OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY"
        # Convert named parameters to positional for pyodbc
        param_values = params

    logger.debug(f"Paginated SQL: {paginated_sql}")

    # Build COUNT query to get total records
    # Extract the main query before ORDER BY for counting
    import re
    # Remove ORDER BY clause for count query
    count_sql = re.sub(r'\s+ORDER\s+BY\s+.*$', '', sql, flags=re.IGNORECASE)
    # Wrap in COUNT(*)
    count_query = f"SELECT COUNT(*) as total FROM ({count_sql}) count_subquery"

    logger.debug(f"Count SQL: {count_query}")

    # Execute query based on database type
    db = None
    rows = []
    total_records = 0
    try:
        if dbtype == "oracle":
            from .db_oracle import OracleDB
            cfg = get_oracle_config(request.server)
            db = OracleDB(cfg)
            # Get total count first
            count_result = db.query(count_query, param_values)
            total_records = count_result[0]['TOTAL'] if count_result else 0
            # Get paginated results
            rows = db.query(paginated_sql, param_values)

        elif dbtype == "mysql":
            cfg = get_mysql_config(request.server)
            db = MySQLDB(cfg)
            # Get total count first
            count_result = db.query(count_query, param_values)
            total_records = count_result[0]['total'] if count_result else 0
            # Get paginated results
            rows = db.query(paginated_sql, param_values)

        elif dbtype == "postgres":
            cfg = get_pg_config(request.server)
            db = PostgresDB(cfg)
            # Get total count first
            count_result = db.query(count_query, param_values)
            total_records = count_result[0]['total'] if count_result else 0
            # Get paginated results
            rows = db.query(paginated_sql, param_values)

        elif dbtype == "mssql":
            from .db_mssql import MSSQLDB
            cfg = get_mssql_config(request.server)
            db = MSSQLDB(cfg)
            # Get total count first
            count_result = db.query(count_query, param_values)
            total_records = count_result[0]['total'] if count_result else 0
            # Get paginated results
            rows = db.query(paginated_sql, param_values)

        # Calculate pagination metadata
        record_count = len(rows)
        total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 0
        has_more = record_count == page_size  # If we got a full page, there might be more

        # Return paginated results with metadata
        return {
            "status": "success",
            "dbtype": dbtype,
            "server": request.server or "default",
            "pagination": {
                "page": page,
                "page_size": page_size,
                "record_count": record_count,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_more": has_more,
                "next_page": page + 1 if has_more else None
            },
            "records": rows
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"sqlExec error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
    finally:
        if db:
            db.close()

