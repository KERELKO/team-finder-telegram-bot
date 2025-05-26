from abc import ABC, abstractmethod
from dataclasses import dataclass

from team_bot.domain.entities.users import Team, User


@dataclass(eq=False)
class GroupFilters:
    title__contains: str | None = None
    owner_id: int | None = None


@dataclass(eq=False)
class TeamFilters:
    game_id: int | None = None
    min_rating: int | None = None
    max_rating: int | None = None
    size: int | None = None


@dataclass(eq=False)
class Pagination:
    offset: int = 0
    limit: int = 20


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

    @abstractmethod
    async def get_by_owner_id(self, owner_id: int) -> Team | None:
        ...

    @abstractmethod
    async def delete_by_owner_id(self, owner_id: int) -> bool:
        ...

    @abstractmethod
    async def update_players_count(self, team_id: str, count: int) -> None:
        ...
