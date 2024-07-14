# type: ignore
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.utils import get_user
from src.common.constants import Game
from src.common.di import Container
from src.common.entities import User
from src.common.filters import GroupFilters, Pagination
from src.infra.repositories.base import AbstractGroupRepository


async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user: User | None = await get_user(context)
    if not user:
        await update.message.reply_text(  # type: ignore
            'У тебе ще немає профілю\n'
            'Використай команду /profile щоб створити профіль',
        )
        return
    await update.message.reply_text(
        'Спробую знайти команду згідно твого профілю:\n'
        f'Гра: {Game.as_string(user.game)}\n'
        'Зачекай трішки...',
    )
    filters = GroupFilters(game_code=user.game)
    repo: AbstractGroupRepository = Container.resolve(AbstractGroupRepository)
    groups = await repo.search(filters=filters, pag=Pagination(0, 20))
    if groups:
        group_text = '\n'.join(str(group) for group in groups)
        await update.message.reply_text(
            'Доступні групи:\n'
            f'{group_text}'
        )
    else:
        await update.message.reply_text(
            'Доступних груп для входу поки що немає :( '
            'спробуй створити свою може хтось захоче пограти'
            f'{filters}\n'
        )
