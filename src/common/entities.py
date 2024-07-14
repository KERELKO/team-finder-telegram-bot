from dataclasses import dataclass, field, asdict
from typing import Any
import uuid

from src.common.constants import Game


@dataclass
class User:
    id: int
    username: str
    game: Game

    def asdict(self) -> dict[str, Any]:
        data = asdict(self)
        data['game'] = data['game'].value if not isinstance(data['game'], int) else data['game']
        return data


@dataclass
class Group:
    id: str = field(default_factory=lambda: str(uuid.uuid4()), kw_only=True)
    owner_id: int
    title: str
    size: int
    game: Game
    description: str = ''

    def asdict(self) -> dict[str, Any]:
        data = asdict(self)
        data['game'] = data['game'].value if not isinstance(data['game'], int) else data['game']
        return data
