from dataclasses import dataclass, field
from typing import Any
import uuid

from src.common.constants import Games, Languages


@dataclass
class User:
    id: int
    username: str
    games: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)

    def asdict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'games': self.games,
            'languages': self.languages,
        }


@dataclass
class Group:
    id: str = field(default_factory=lambda: str(uuid.uuid4()), kw_only=True)
    owner_id: int
    title: str
    group_size: int
    game: Games
    language: Languages
    description: str = ''
    is_active: bool = False

    def asdict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'title': self.title,
            'group_size': self.group_size,
            'game': self.game,
            'language': self.language,
            'description': self.description,
            'is_active': self.is_active,
        }
