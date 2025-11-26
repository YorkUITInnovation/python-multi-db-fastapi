import oracledb
from typing import Any, Dict, List, Tuple

class OracleDB:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conn = None

    def connect(self):
        dsn = oracledb.makedsn(
            self.config.get("host"), int(self.config.get("port", 1521)), service_name=self.config.get("service_name")
        )
        self.conn = oracledb.connect(
            user=self.config.get("user"), password=self.config.get("password"), dsn=dsn
        )
        return self.conn

    def query(self, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        if self.conn is None:
            self.connect()
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        cur.close()
        return rows

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
