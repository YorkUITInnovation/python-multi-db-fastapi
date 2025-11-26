import pyodbc
from typing import Any, Dict, List, Tuple

class MSSQLDB:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conn = None

    def connect(self):
        conn_str = (
            f"DRIVER={{{self.config.get('driver', 'ODBC Driver 17 for SQL Server')}}};"
            f"SERVER={self.config.get('server')},{int(self.config.get('port', 1433))};"
            f"DATABASE={self.config.get('db')};"
            f"UID={self.config.get('user')};"
            f"PWD={self.config.get('password')}"
        )
        self.conn = pyodbc.connect(conn_str)
        return self.conn

    def query(self, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        if self.conn is None:
            self.connect()
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [desc[0] for desc in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        cur.close()
        return rows

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
