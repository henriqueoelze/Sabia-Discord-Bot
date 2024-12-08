
import json
import os
from typing import Optional

import aiosqlite
from gateways.persistence._interface import PersistenceGateway
from models.proxy import Proxy

_TABLE_MIGRATION = 'CREATE TABLE IF NOT EXISTS proxy(server_id INTEGER PRIMARY KEY, proxy_data TEXT)'
_INSERT_SQL = 'INSERT INTO proxy VALUES (?, ?) ON CONFLICT(server_id) DO UPDATE SET proxy_data=excluded.proxy_data'
_SELECT_SQL = 'SELECT proxy_data FROM proxy WHERE server_id = ?'


class SqlLitePersistenceGatewayImpl(PersistenceGateway):
    def __init__(self):
        DATABASE_NAME = os.getenv('DATABASE_NAME')
        self.database_name = DATABASE_NAME

    async def store_proxy(
        self,
        server_id: int,
        proxy: Proxy,
    ):
        proxy_json: str = json.dumps(proxy.__dict__)

        async with self.get_connection() as db:
            insert_params = (server_id, proxy_json,)
            await db.execute(_INSERT_SQL, insert_params)

    async def get_proxy(self, server_id: int) -> Proxy:
        proxy_str: Optional[str] = None
        async with self.get_connection() as db:
            query_params = (server_id,)
            async with db.execute(_SELECT_SQL, query_params) as cursor:
                async for row in cursor:
                    proxy_str = row[0]

        if proxy_str is None:
            return Proxy()

        loaded_json: Proxy = json.loads(proxy_str)
        server_proxy = Proxy(**loaded_json)
        return server_proxy

    def get_connection(self) -> aiosqlite.Connection:
        return aiosqlite.connect(self.database_name)
