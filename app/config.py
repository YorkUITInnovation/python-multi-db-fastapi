from dotenv import load_dotenv
import os
import json
from typing import List, Dict, Any
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_MODE = os.getenv("APP_MODE", "DEV").upper()

# API Keys: support single API_KEY or JSON/CSV API_KEYS
_api_keys_raw = os.getenv("API_KEYS")
API_KEYS: List[str] = []
if _api_keys_raw:
    parsed = None
    # Try JSON first
    try:
        parsed = json.loads(_api_keys_raw)
    except Exception:
        # Try CSV (comma-separated keys)
        if "," in _api_keys_raw:
            parsed = [k.strip() for k in _api_keys_raw.split(",") if k.strip()]
    if isinstance(parsed, list):
        if parsed and isinstance(parsed[0], dict) and "key" in parsed[0]:
            API_KEYS = [k["key"] for k in parsed if isinstance(k, dict) and "key" in k]
        else:
            API_KEYS = [k for k in parsed if isinstance(k, str) and k]
    else:
        logger.warning("Invalid API_KEYS format; expected JSON array or comma-separated string. Falling back to API_KEY.")

if not API_KEYS:
    ak = os.getenv("API_KEY")
    if ak:
        API_KEYS = [ak]

# Helper to parse JSON env safely

def _parse_json_env(name: str):
    raw = os.getenv(name)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"Invalid JSON in {name}: {e}")
        return None

# Single DB configs (backward-compatible)
ORACLE_CONFIG = {
    "host": os.getenv("ORACLE_HOST"),
    "port": int(os.getenv("ORACLE_PORT", "1521")),
    "service_name": os.getenv("ORACLE_SERVICE_NAME"),
    "user": os.getenv("ORACLE_USER"),
    "password": os.getenv("ORACLE_PASSWORD"),
}

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "db": os.getenv("MYSQL_DB"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
}

MSSQL_CONFIG = {
    "driver": os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server"),
    "server": os.getenv("MSSQL_SERVER"),
    "port": int(os.getenv("MSSQL_PORT", "1433")),
    "db": os.getenv("MSSQL_DB"),
    "user": os.getenv("MSSQL_USER"),
    "password": os.getenv("MSSQL_PASSWORD"),
}

PG_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "port": int(os.getenv("PG_PORT", "5432")),
    "db": os.getenv("PG_DB"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
}

# Multi-DB configs via JSON objects keyed by name
# Example: MYSQL_CONFIGS={"primary":{"host":"...","port":3306,"db":"...","user":"...","password":"..."},"analytics":{...}}
MYSQL_CONFIGS: Dict[str, Dict[str, Any]] = _parse_json_env("MYSQL_CONFIGS") or {}
PG_CONFIGS: Dict[str, Dict[str, Any]] = _parse_json_env("PG_CONFIGS") or {}
MSSQL_CONFIGS: Dict[str, Dict[str, Any]] = _parse_json_env("MSSQL_CONFIGS") or {}
ORACLE_CONFIGS: Dict[str, Dict[str, Any]] = _parse_json_env("ORACLE_CONFIGS") or {}

# Utility to pick config by name with fallback to single-config

def get_mysql_config(name: str | None) -> Dict[str, Any]:
    if name and name in MYSQL_CONFIGS:
        return MYSQL_CONFIGS[name]
    return MYSQL_CONFIG

def get_pg_config(name: str | None) -> Dict[str, Any]:
    if name and name in PG_CONFIGS:
        return PG_CONFIGS[name]
    return PG_CONFIG

def get_mssql_config(name: str | None) -> Dict[str, Any]:
    if name and name in MSSQL_CONFIGS:
        return MSSQL_CONFIGS[name]
    return MSSQL_CONFIG

def get_oracle_config(name: str | None) -> Dict[str, Any]:
    if name and name in ORACLE_CONFIGS:
        return ORACLE_CONFIGS[name]
    return ORACLE_CONFIG
