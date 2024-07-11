from dataclasses import dataclass

from src.common.constants import Games, Languages


@dataclass(eq=False)
class GroupFilters:
    title__contains: str | None = None
    game: Games | None = None
    language: Languages | None = None
    size: int | None = None
