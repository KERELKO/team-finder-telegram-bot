from telegram import Message
from telegram.ext import filters


class ListFilter(filters.MessageFilter):
    def __init__(self, items: list[str]) -> None:
        self.items = items
        super().__init__(name=f"ListFilter({self.items})", data_filter=True)

    def filter(self, message: Message) -> bool:
        return message.text in self.items
