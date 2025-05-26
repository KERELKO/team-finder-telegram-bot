from typing import Any

from telegram import Message
from telegram.ext import filters

from team_bot.domain.entities.games.base import GameCollection


class ListFilter(filters.MessageFilter):
    """Checks if `message.text` in the list"""

    def __init__(self, items: list[Any]) -> None:
        self.items = items
        super().__init__(name=f'{self.__class__.__name__}({self.items})', data_filter=True)

    def filter(self, message: Message) -> bool:
        return message.text in self.items


class GameRanksFilter(filters.MessageFilter):
    """Check if `message.text` is a game rank"""

    def __init__(
        self, game_collection: GameCollection,
    ) -> None:
        super().__init__(name=f'{self.__class__.__name__}', data_filter=True)
        self.game_collection = game_collection

    def filter(self, message: Message) -> bool:
        for game in self.game_collection:
            for rank in game.ranks().values():  # type: ignore
                if rank == message.text:
                    return True
        return False
