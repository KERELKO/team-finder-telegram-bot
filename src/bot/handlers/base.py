# type: ignore
from abc import ABC, abstractmethod

from telegram import ForceReply, Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.constants import START_TEXT, HELP_TEXT


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        START_TEXT,
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


class BaseConversationHandler(ABC):
    @classmethod
    @abstractmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ...

    @classmethod
    async def cancel_command(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            'Розмова перервана ', reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
