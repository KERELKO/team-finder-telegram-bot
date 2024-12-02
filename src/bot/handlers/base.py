from abc import ABC, abstractmethod

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.constants import CANCEL_TEXT


class BaseConversationHandler(ABC):
    @classmethod
    @abstractmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ...

    @classmethod
    async def cancel_command(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(  # type: ignore
            CANCEL_TEXT, reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
