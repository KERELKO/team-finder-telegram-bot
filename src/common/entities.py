from dataclasses import dataclass, field
from typing import Any
import uuid

from src.common.constants import Game, Language


@dataclass
class User:
    id: int
    username: str
    game: Game
    language: Language

    def asdict(self) -> dict[str, Any]:
        data = {
            'id': self.id,
            'username': self.username,
            'game': self.game,
            'language': self.language,
        }
        return data


@dataclass
class Group:
    id: str = field(default_factory=lambda: str(uuid.uuid4()), kw_only=True)
    owner_id: int
    title: str
    size: int
    game: Game
    language: Language
    description: str = ''

    def asdict(self) -> dict[str, Any]:
        data = {
            'id': self.id,
            'owner_id': self.owner_id,
            'title': self.title,
            'size': self.size,
            'game': self.game,
            'language': self.language,
            'description': self.description,
        }
        return data
