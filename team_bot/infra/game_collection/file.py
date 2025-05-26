import json
from functools import cache
from pathlib import Path
from typing import Any

from team_bot.domain.entities.games.base import BaseGame, GameCollection


class FileGameCollection(GameCollection):
    game_id: int = 1

    def __init__(self, path: Path | str) -> None:
        self.games: list[BaseGame] = self.load(path)
        self.i = 0

    def __next__(self):
        try:
            item = self.games[self.i]
            self.i += 1
            return item
        except IndexError:
            raise StopIteration

    @classmethod
    def _create_game_instance(cls, game_name: str, json_ranks: dict[str, str]) -> BaseGame:

        game = BaseGame(
            id=cls.game_id,
            name=game_name,
            _ranks={int(k): v for k, v in json_ranks.items()},
        )
        cls.game_id += 1

        return game

    @classmethod
    def _get_game_list_from_json(cls, data: dict[str, Any]) -> list[BaseGame]:
        games = []
        for key, value in data.items():
            games.append(cls._create_game_instance(key, value['ranks']))
        return games

    @classmethod
    @cache
    def load(cls, path: Path | str) -> list[BaseGame]:
        games: list[BaseGame] = []
        with open(path, 'r') as file:
            loaded_data = json.load(file)
            games = cls._get_game_list_from_json(loaded_data)
        return games
