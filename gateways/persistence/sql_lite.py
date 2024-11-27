
import json
import os
from typing import Optional
from gateways.persistence._interface import PersistenceGateway
from models.proxy import Proxy

import sqlite3

_TABLE_MIGRATION = 'CREATE TABLE IF NOT EXISTS proxy(server_id INTEGER PRIMARY KEY, proxy_data TEXT)'
_INSERT_SQL = 'INSERT INTO proxy VALUES (?, ?) ON CONFLICT(server_id) DO UPDATE SET proxy_data=excluded.proxy_data'
_SELECT_SQL = 'SELECT proxy_data FROM proxy WHERE server_id = ?'


class SqlLitePersistenceGatewayImpl(PersistenceGateway):
    def __init__(self):
        DATABASE_NAME = os.getenv('DATABASE_NAME')

        connection = sqlite3.connect(DATABASE_NAME)
        migration_cursor: sqlite3.Cursor = connection.cursor()

        migration_cursor.execute(_TABLE_MIGRATION)
        migration_cursor.close()

        self.connection: sqlite3.Connection = connection

    def store_proxy(
        self,
        server_id: int,
        proxy: Proxy,
    ):
        proxy_json: str = json.dumps(proxy.__dict__)

        with self.connection:
            insert_params = (server_id, proxy_json,)
            self.connection.execute(_INSERT_SQL, insert_params)

    def get_proxy(self, server_id: int) -> Proxy:
        proxy_str: Optional[str] = None
        with self.connection:
            query_params = (server_id,)
            query = self.connection.execute(_SELECT_SQL, query_params)
            result = query.fetchone()
            if result is not None and len(result) > 0:
                proxy_str = result[0]

        if proxy_str is None:
            return Proxy()

        loaded_json: Proxy = json.loads(proxy_str)
        server_proxy = Proxy(**loaded_json)
        return server_proxy
