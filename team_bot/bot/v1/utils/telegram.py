from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from team_bot.bot.v1.constants import BotCommand
from team_bot.infra.di import Container
from team_bot.domain.entities.users import User
from team_bot.infra.repositories.base import AbstractUserRepository


async def get_user(context: ContextTypes.DEFAULT_TYPE) -> User | None:
    repo: AbstractUserRepository = Container.resolve(AbstractUserRepository)
    user: User | None = await repo.get_by_id(id=context._user_id)  # type: ignore
    return user


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
            f'Використай команду /{BotCommand.CREATE_PROFILE} щоб створити профіль',
        )
        return ConversationHandler.END
    if user_context:
        context.user_data['user'] = user  # type: ignore
    return user
