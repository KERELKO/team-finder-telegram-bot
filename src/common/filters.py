from dataclasses import dataclass

from src.common.constants import Game, Language


@dataclass(eq=False)
class GroupFilters:
    game: Game | None = None
    language: Language | None = None
    size: int | None = None


@dataclass(eq=False)
class Pagination:
    offset: int = 0
    limit: int = 20
