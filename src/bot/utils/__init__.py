from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.common.di import Container
from src.common.entities import User
from src.infra.repositories.base import AbstractUserRepository


async def get_user(context: ContextTypes.DEFAULT_TYPE) -> User | None:
    repo: AbstractUserRepository = Container.resolve(AbstractUserRepository)
    user: User | None = await repo.get_by_id(id=context._user_id)  # type: ignore
    return user if user else None


async def get_user_or_end_conversation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_context: bool = True,
) -> User | int:
    """
    Returns `User` instance or `ConversationHandler.END`,
    also adds user instance to the `context`
    ### It won't permanently stop the conversation if user is not found!
    """
    repo: AbstractUserRepository = Container.resolve(AbstractUserRepository)
    user: User | None = await repo.get_by_id(id=context._user_id)  # type: ignore
    if user is None:
        await update.message.reply_text(  # type: ignore
            'У тебе ще немає профілю\n'
            'Використай команду /profile щоб створити профіль',
        )
        return ConversationHandler.END
    if user_context:
        context.user_data['user'] = user  # type: ignore
    return user


__all__ = ['get_user_or_end_conversation', 'get_user']
