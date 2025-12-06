import oracledb
from typing import Any, Dict, List, Tuple
import logging
import os

logger = logging.getLogger(__name__)

# Try to initialize thick mode for Oracle connections
# This is needed for older Oracle password verifier types (like 0x939)
_thick_mode_initialized = False
_thick_mode_error = None

try:
    # Check if ORACLE_CLIENT_LIB environment variable is set
    lib_dir = os.getenv("ORACLE_CLIENT_LIB")
    if lib_dir:
        oracledb.init_oracle_client(lib_dir=lib_dir)
    else:
        oracledb.init_oracle_client()
    _thick_mode_initialized = True
    logger.info("Oracle client initialized in thick mode")
except Exception as e:
    _thick_mode_error = str(e)
    logger.warning(f"Oracle thick mode not available: {e}")
    logger.warning("Using thin mode - some older Oracle password types may not be supported")
    logger.info("To enable thick mode, install Oracle Instant Client and set ORACLE_CLIENT_LIB environment variable")

class OracleDB:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conn = None

    def connect(self):
        try:
            # Support direct DSN string or build from components
            if "dsn" in self.config and self.config["dsn"]:
                dsn = self.config["dsn"]
                logger.info(f"Using provided DSN connection string")
            else:
                # Build DSN from host, port, service_name
                host = self.config.get("host")
                port = int(self.config.get("port", 1521))
                service_name = self.config.get("service_name")
                logger.info(f"Building DSN: host={host}, port={port}, service_name={service_name}")
                dsn = oracledb.makedsn(host, port, service_name=service_name)

            user = self.config.get("user")
            password = self.config.get("password")

            logger.info(f"Attempting Oracle connection with user={user} (thick_mode={_thick_mode_initialized})")
            self.conn = oracledb.connect(user=user, password=password, dsn=dsn)
            logger.info("Oracle connection successful")
            return self.conn
        except oracledb.NotSupportedError as e:
            error_msg = str(e)
            if "DPY-3015" in error_msg or "password verifier" in error_msg:
                logger.error(f"Oracle password verifier not supported in thin mode: {e}")
                logger.error("SOLUTION: Install Oracle Instant Client to enable thick mode")
                logger.error("  1. Download from: https://www.oracle.com/database/technologies/instant-client/downloads.html")
                logger.error("  2. Extract and set ORACLE_CLIENT_LIB environment variable to the lib directory")
                logger.error("  3. Example: export ORACLE_CLIENT_LIB=/opt/oracle/instantclient_21_1")
                raise RuntimeError(
                    f"Oracle connection failed due to unsupported password verifier type. "
                    f"Install Oracle Instant Client and set ORACLE_CLIENT_LIB environment variable. "
                    f"Details: {e}"
                ) from e
            else:
                raise RuntimeError(f"Oracle connection failed: {e}") from e
        except Exception as e:
            logger.error(f"Oracle connection failed: {e}")
            logger.error(f"Config (masked): user={self.config.get('user')}, has_password={bool(self.config.get('password'))}, has_dsn={bool(self.config.get('dsn'))}")
            raise RuntimeError(f"Oracle connection failed: {e}") from e

    def query(self, sql: str, params: Tuple | Dict[str, Any] = ()) -> List[Dict[str, Any]]:
        try:
            if self.conn is None:
                logger.info("No existing connection, connecting to Oracle...")
                self.connect()
            logger.debug(f"Executing query: {sql}")
            logger.debug(f"Parameters: {params}")
            cur = self.conn.cursor()
            # Oracle supports both positional (tuple) and named (dict) parameters
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            cur.close()
            logger.debug(f"Query returned {len(rows)} rows")
            return rows
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def close(self):
        if self.conn:
            logger.debug("Closing Oracle connection")
            self.conn.close()
            self.conn = None
