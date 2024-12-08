from abc import ABC, abstractmethod

from models.proxy import Proxy


class PersistenceGateway(ABC):
    @abstractmethod
    async def store_proxy(
        self,
        server_id: int,
        proxy: Proxy,
    ): raise NotImplementedError

    @abstractmethod
    async def get_proxy(self, server_id: int) -> Proxy: raise NotImplementedError
