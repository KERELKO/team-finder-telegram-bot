from dataclasses import dataclass


@dataclass(eq=False)
class GroupFilters:
    game_code: int | None = None
    language_code: int | None = None
    size: int | None = None


@dataclass(eq=False)
class Pagination:
    offset: int = 0
    limit: int = 20
