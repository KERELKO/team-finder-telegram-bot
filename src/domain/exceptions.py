from dataclasses import dataclass

from src.domain.entities.games.base import AbstractGame


class DomainException(Exception):
    ...


@dataclass(eq=False)
class GameNotFoundException(DomainException):
    game_id: int


@dataclass(eq=False)
class InvalidGameRank(DomainException):
    game: AbstractGame
    key: int
