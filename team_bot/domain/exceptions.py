from dataclasses import dataclass

from team_bot.domain.entities.games.base import BaseGame


class DomainException(Exception):
    ...


@dataclass(eq=False)
class GameNotFoundException(DomainException):
    game_id: int


@dataclass(eq=False)
class InvalidGameRank(DomainException):
    game: BaseGame
    key: int
