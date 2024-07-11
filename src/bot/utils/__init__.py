from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.common.di import Container
from src.common.entities import User
from src.infra.repositories.base import AbstractUserRepository


async def get_user_or_end_conversation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
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
            'You are not registered yet\n'
            'please type /profile to create your first profile',
        )
        return ConversationHandler.END
    context.user_data['user'] = user  # type: ignore
    return user


__all__ = ['get_user_or_end_conversation']
