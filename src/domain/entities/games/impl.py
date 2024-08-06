
from typing import Any

from .base import AbstractGame, AbstractGames


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


class GamesFromClasses(AbstractGames):
    def __init__(self) -> None:
        self.games: list[type[AbstractGame]] = [AOE2, CS2]
        self.i = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = self.games[self.i]
            self.i += 1
            return item
        except IndexError:
            raise StopIteration

    @classmethod
    def factory(cls) -> list[type[AbstractGame]]:
        return [g for g in GamesFromClasses()]


class GamesFromFile(AbstractGames):
    def __init__(self) -> None:
        self.games: list[type[AbstractGame]] = [AOE2, CS2]

    def __iter__(self):
        return self

    def __next__(self):
        i = 0
        try:
            item = self.games[i]
            i += 1
            return item
        except IndexError:
            raise StopIteration

    @staticmethod
    def _create_game_from_dict(data: dict[str, Any]) -> AbstractGame:
        ...

    @staticmethod
    def _create_games_from_json(data) -> list[type[AbstractGame]]:
        ...

    @classmethod
    def factory(cls) -> list[type[AbstractGame]]:
        return [g for g in GamesFromClasses().games]
