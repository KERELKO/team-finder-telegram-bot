from abc import ABC, abstractmethod
from dataclasses import dataclass


class AbstractGame(ABC):
    id: int
    name: str

    @classmethod
    @abstractmethod
    def ranks(cls, codes: bool = False) -> dict[int, str] | list[int]:
        ...


class AbstractGames(ABC):
    """Base class that allows to iterate through games

    type of game: `AbstractGame`

    """

    @abstractmethod
    def __iter__(self) -> 'AbstractGames':
        return self

    @abstractmethod
    def __next__(self) -> type[AbstractGame]:
        ...


@dataclass(frozen=True, eq=False)
class GameData:
    id: int
    rating: int
