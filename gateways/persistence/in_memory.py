
from gateways.persistence._interface import PersistenceGateway
from models.proxy import Proxy


class InMemoryPersistenceGatewayImpl(PersistenceGateway):
    def __init__(self):
        self.db: dict[int, Proxy] = {}

    def store_proxy(
        self,
        server_id: int,
        proxy: Proxy,
    ):
        self.db[server_id] = proxy

    def get_proxy(self, server_id: int) -> Proxy:
        return self.db[server_id] if server_id in self.db else Proxy()
