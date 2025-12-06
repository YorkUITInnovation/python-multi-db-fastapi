import psycopg2
from typing import Any, Dict, List, Tuple

class PostgresDB:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.config.get("host"),
            port=int(self.config.get("port", 5432)),
            dbname=self.config.get("db"),
            user=self.config.get("user"),
            password=self.config.get("password"),
        )
        return self.conn

    def query(self, sql: str, params: Tuple | Dict[str, Any] = ()) -> List[Dict[str, Any]]:
        if self.conn is None:
            self.connect()
        cur = self.conn.cursor()
        # PostgreSQL supports both positional (tuple) and named (dict with %(name)s syntax)
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        cols = [desc[0] for desc in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        cur.close()
        return rows

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
