# type: ignore
import asyncio
import random

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.utils import get_user
from src.common.di import Container
from src.domain.entities import User
from src.common.filters import TeamFilters, Pagination
from src.infra.repositories.base import AbstractTeamRepository


async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user: User | None = await get_user(context)
    if not user:
        await update.message.reply_text(  # type: ignore
            'У тебе ще немає профілю\n'
            'Використай команду /profile щоб створити профіль',
        )
        return
    await update.message.reply_text(
        'Спробую знайти команду згідно твого профілю\n'
        'Зачекай трішки...',
    )
    filters = TeamFilters(
        game_id=user.games[0].id,
        min_rating=user.games[0].rating - 1,
        max_rating=user.games[0].rating + 1,
    )
    repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
    groups = await repo.search(filters=filters, pag=Pagination(0, 20))
    await asyncio.sleep(random.randint(2, 3))
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
