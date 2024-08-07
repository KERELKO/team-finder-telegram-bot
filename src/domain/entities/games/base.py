from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(eq=False)
class AbstractGame(ABC):
    id: int
    name: str = ''

    @classmethod
    @abstractmethod
    def ranks(cls, codes: bool = False) -> dict[int, str] | list[int]:
        ...

    def __eq__(self, other: 'AbstractGame') -> bool:
        return self.id == other.id


class AbstractGames(ABC):
    """Base class that allows to iterate through all available games

    type of game: `AbstractGame`

    """

    def __iter__(self) -> 'AbstractGames':
        return self

    @abstractmethod
    def __next__(self) -> type[AbstractGame]:
        ...

    @classmethod
    @abstractmethod
    def factory(cls) -> list[AbstractGame]:
        ...


@dataclass(frozen=True, eq=False)
class GameData:
    id: int
    rating: int
