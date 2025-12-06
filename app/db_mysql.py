import mysql.connector
from typing import Any, Dict, List, Tuple

class MySQLDB:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conn = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.config["host"],
            port=self.config["port"],
            database=self.config["db"],
            user=self.config["user"],
            password=self.config["password"],
        )
        return self.conn

    def query(self, sql: str, params: Tuple | Dict[str, Any] = ()) -> List[Dict[str, Any]]:
        if self.conn is None:
            self.connect()
        cur = self.conn.cursor()
        # MySQL supports both positional (tuple) and named (dict with %(name)s syntax)
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        cur.close()
        return rows

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
