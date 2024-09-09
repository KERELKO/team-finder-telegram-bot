from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(eq=False)
class AbstractGame(ABC):
    id: int
    name: str = field(default='', kw_only=True)

    @classmethod
    @abstractmethod
    def ranks(cls, codes: bool = False) -> dict[int, str] | list[int]:
        ...


class Games(ABC):
    """Base class that allows to iterate through all available games

    type of game: `AbstractGame`

    """

    def __iter__(self) -> 'Games':
        return self

    @abstractmethod
    def __next__(self) -> AbstractGame:
        ...

    @classmethod
    @abstractmethod
    def factory(cls) -> list[AbstractGame]:
        ...


@dataclass(frozen=True, eq=False)
class GameData:
    id: int
    rating: int


@dataclass(eq=False)
class _Game(AbstractGame):
    _ranks: dict[int, str]

    def __eq__(self, other: 'AbstractGame') -> bool:
        return self.id == other.id

    def ranks(self, codes: bool = False) -> dict[int, str] | list[int]:
        if codes:
            return list(self._ranks.keys())
        return self._ranks
