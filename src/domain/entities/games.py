from abc import ABC, abstractmethod
from dataclasses import dataclass


class AbstractGame(ABC):
    id: int
    name: str

    @classmethod
    @abstractmethod
    def ranks(cls, codes: bool = False) -> dict[int, str] | list[int]:
        ...


class CS2(AbstractGame):
    id: int = 1
    name: str = 'Counter Strike 2'

    @classmethod
    def ranks(cls, codes: bool = False) -> dict[int, str] | list[int]:
        data = {
            1: 'Silver',
            2: 'Gold Nova',
            3: 'Master Guardian',
            4: 'Legendary Eagle',
            5: 'Global Elite',
        }
        if codes:
            return list(data.keys())
        return data


class AOE2(AbstractGame):
    id: int = 2
    name: str = 'Age of empires 2'

    @classmethod
    def ranks(cls, codes: bool = False) -> dict[int, str] | list[int]:
        data = {
            1: '600',
            2: '800',
            3: '1000',
            4: '1200',
            5: '1400',
            6: '1600',
            7: '1800',
            8: '2000',
        }
        if codes:
            return list(data.keys())
        return data


@dataclass(frozen=True)
class Game:
    id: int
    rating: int


def games() -> list[type[AbstractGame]]:
    return [g for g in (AOE2, CS2)]


def get_game_by_id(game_id: int) -> type[AbstractGame] | None:
    for game in games():
        if game.id == game_id:
            return game
    return None


def get_game_by_name(game_name: str) -> type[AbstractGame] | None:
    for game in games():
        if game.name == game_name:
            return game
    return None


def get_game_rank_value(game: AbstractGame, key: int) -> str:
    for _key, value in game.ranks().items():  # type: ignore
        if _key == key:
            return value
    return 'N/D'
