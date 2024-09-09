import json

from functools import cache
from typing import Any

from src.common.config import get_conf

from .base import AbstractGame, Games, _Game


CS2 = _Game(
    id=1,
    name='Counter Strike 2',
    _ranks={
        1: 'Silver',
        2: 'Gold Nova',
        3: 'Master Guardian',
        4: 'Legendary Eagle',
        5: 'Global Elite',
    }
)

AOE2 = _Game(
    id=2,
    name='Age of empires 2',
    _ranks={
        1: '600',
        2: '800',
        3: '1000',
        4: '1200',
        5: '1400',
        6: '1600',
        7: '1800',
        8: '2000',
    },
)


class GamesFromClasses(Games):
    def __init__(self, games: list[AbstractGame] | None = None) -> None:
        self.games = games or [AOE2, CS2]
        self.i = 0

    def __next__(self) -> AbstractGame:
        try:
            item = self.games[self.i]
            self.i += 1
            return item
        except IndexError:
            raise StopIteration

    @classmethod
    def factory(cls) -> list[AbstractGame]:
        return [g for g in cls()]


class GamesFromFile(Games):
    game_id: int = 1

    def __init__(self) -> None:
        self.games: list[AbstractGame] = self._get_games_from_file()
        self.i = 0

    def __next__(self):
        try:
            item = self.games[self.i]
            self.i += 1
            return item
        except IndexError:
            raise StopIteration

    @classmethod
    def _create_game_instance(cls, game_name: str, json_ranks: dict[str, str]) -> AbstractGame:

        game = _Game(
            id=cls.game_id,
            name=game_name,
            _ranks={int(k): v for k, v in json_ranks.items()},
        )
        cls.game_id += 1

        return game

    @classmethod
    def _get_game_list_from_json(cls, data: dict[str, Any]) -> list[AbstractGame]:
        games = []
        for key, value in data.items():
            games.append(cls._create_game_instance(key, value['ranks']))
        return games

    @classmethod
    @cache
    def _get_games_from_file(cls) -> list[AbstractGame]:
        games: list[AbstractGame] = []
        with open(get_conf().games_json_path, 'r') as file:
            loaded_data = json.load(file)
            games = cls._get_game_list_from_json(loaded_data)
        return games

    @classmethod
    def factory(cls) -> list[AbstractGame]:
        return cls._get_games_from_file()
