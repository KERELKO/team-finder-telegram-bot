from dataclasses import dataclass


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
