import asyncio
import random

from telegram import ForceReply, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.bot.constants import HELP_TEXT, START_TEXT, BotCommands, TeamInfoTextHTML
from src.bot.utils import get_user
from src.common.config import get_conf
from src.common.di import Container
from src.common.filters import Pagination, TeamFilters
from src.common.utils import get_game_by_id, get_game_rank_value
from src.domain.entities import Team, User
from src.domain.entities.games.base import AbstractGame
from src.domain.exceptions import GameNotFoundException, InvalidGameRank
from src.infra.repositories.base import AbstractTeamRepository


async def find_team_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user: User | None = await get_user(context)
    if not user:
        await update.message.reply_text(  # type: ignore
            'У тебе ще немає профілю\n'
            f'Використай команду /{BotCommands.CREATE_PROFILE} щоб створити профіль',
        )
        return
    await update.message.reply_text(  # type: ignore
        'Спробую знайти команду згідно твого профілю\n'
        'Зачекай трішки...',
    )
    offset = get_conf().RATING_OFFSET
    filters = TeamFilters(
        game_id=user.games[0].id,
        min_rating=user.games[0].rating - offset,
        max_rating=user.games[0].rating + offset,
    )
    repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
    teams: list[Team] = await repo.search(filters=filters, pag=Pagination(0, 20))
    await asyncio.sleep(random.randint(2, 3))
    if not teams:
        await update.message.reply_text(  # type: ignore
            'Доступних команд для входу поки що немає :(\n'
            'спробуй створити свою, може хтось захоче пограти'
        )
        return
    await update.message.reply_text('Доступні команди:\n')  # type: ignore
    for team in teams:
        game: AbstractGame | None = get_game_by_id(team.game_id)
        if not game:
            raise GameNotFoundException(team.game_id)
        rank_value = get_game_rank_value(game, team.game_rating)
        if not rank_value:
            raise InvalidGameRank(game, team.game_rating)
        text = TeamInfoTextHTML(
            url=team.id,
            title=team.title,
            game=game.name,
            skill=rank_value,
            players_to_fill=team.players_to_fill,
            description=team.description,
            preface='',
        )
        await update.message.reply_text(  # type: ignore
            str(text),
            parse_mode=ParseMode.HTML
        )


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(  # type: ignore
        START_TEXT,
        reply_markup=ForceReply(selective=True),
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)  # type: ignore
