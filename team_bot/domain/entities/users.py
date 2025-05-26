from dataclasses import dataclass, field


# Value Object
@dataclass(frozen=True, eq=False, slots=True)
class GameData:
    id: int
    rating: int


@dataclass
class User:
    id: int
    username: str
    games: list[GameData] = field(default_factory=list)


@dataclass(kw_only=True)
class Group:
    id: str
    owner_id: int
    title: str
    description: str = ''


@dataclass
class Team(Group):
    players_to_fill: int
    game_id: int
    game_rating: int
