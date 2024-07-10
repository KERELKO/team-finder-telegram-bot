from dataclasses import dataclass

from src.common.constants import Games, Languages


@dataclass
class User:
    id: int
    games: list[str]
    username: str
    languages: list[str]


@dataclass
class Group:
    owner_id: int
    title: str
    group_size: int
    game: Games
    language: Languages
    description: str = ''
    is_active: bool = False
