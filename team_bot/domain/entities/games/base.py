from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(eq=False)
class BaseGame(ABC):
    id: int
    _ranks: dict[int, str]
    name: str = field(default='', kw_only=True)

    def __eq__(self, other) -> bool:
        return self.id == other.id if isinstance(other, BaseGame) else False

    def ranks(self, codes: bool = False) -> dict[int, str] | list[int]:
        if codes:
            return list(self._ranks.keys())
        return self._ranks


class GameCollection(ABC):
    """Base class that allows to iterate through all available games

    type of game: `BaseGame`

    """

    def __iter__(self) -> 'GameCollection':
        return self

    @abstractmethod
    def __next__(self) -> BaseGame:
        ...
