from abc import ABC, abstractmethod

from src.domain.entities import Team, User
from src.common.filters import TeamFilters, Pagination


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> User | None:
        ...

    @abstractmethod
    async def add(self, user: User) -> User:
        ...


class AbstractTeamRepository(ABC):
    @abstractmethod
    async def add(self, team: Team) -> Team:
        ...

    @abstractmethod
    async def search(self, filters: TeamFilters, pag: Pagination) -> list[Team]:
        ...
