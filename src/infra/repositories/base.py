from abc import ABC, abstractmethod

from src.common.entities import Group, User
from src.common.filters import GroupFilters, Pagination


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> User | None:
        ...

    @abstractmethod
    async def add(self, user: User) -> User:
        ...


class AbstractGroupRepository(ABC):
    @abstractmethod
    async def add(self, group: Group) -> Group:
        ...

    @abstractmethod
    async def get_by_filters(self, filters: GroupFilters, pag: Pagination) -> list[Group]:
        ...
