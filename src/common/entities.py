from dataclasses import dataclass, field

from src.common.constants import Games, Languages


@dataclass
class User:
    id: int
    username: str
    games: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)


@dataclass
class Group:
    owner_id: int
    title: str
    group_size: int
    game: Games
    language: Languages
    description: str = ''
    is_active: bool = False
