import uuid
from dataclasses import dataclass, field

from .games import Game


@dataclass
class User:
    id: int
    username: str
    games: list[Game] = field(default_factory=list)


@dataclass(kw_only=True)
class Group:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: int
    title: str
    description: str = ''


@dataclass
class Team(Group):
    players_to_fill: int
    game_id: int
    game_rating: int
