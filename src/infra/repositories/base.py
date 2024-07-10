from abc import ABC, abstractmethod

from src.common.entities import User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> User:
        ...

    @abstractmethod
    async def add(self, user: User) -> User:
        ...
