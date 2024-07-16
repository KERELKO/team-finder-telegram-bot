# type: ignore
from enum import Enum

from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from src.bot.constants import TeamInfoTextHTML
from src.common.di import Container
from src.domain.entities import User, Team
from src.domain.entities.games import games, get_game_by_name, AbstractGame, Game, get_game_by_id
from src.infra.repositories.base import AbstractUserRepository, AbstractTeamRepository
from src.bot.filters import ListFilter, GameRanksFilter
from src.bot.utils.parsers import parse_telegram_webpage
from src.bot.utils import get_user_or_end_conversation

from .base import BaseConversationHandler


class CollectUserDataHandler(BaseConversationHandler):
    """
    ### Aggregate handlers into ConversationHandler
    Collect -> Game -> Language -> Skill
    """

    class Handlers(int, Enum):
        start_conversation = 0
        game = 1
        rating = 2

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        choices: list[list[str]] = [[game.name for game in games()]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            one_time_keyboard=True,
            input_field_placeholder='Гра',
        )
        await update.message.reply_text(
            'Зараз мені потрібно дізнатись більше про тебе, скажи в які ігри зі списку ти граєш?',
            reply_markup=buttons,
        )
        return cls.Handlers.game

    @classmethod
    async def game_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        game = get_game_by_name(update.message.text)
        context.user_data['game_id'] = game.id

        choices: list[list[str]] = [[k for k in game.ranks().values()]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text(
            'На якому рівні ти граєш?',
            reply_markup=buttons,
        )
        return cls.Handlers.rating

    @classmethod
    async def rating_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        for code, value in get_game_by_id(context.user_data['game_id']).ranks().items():
            if value == update.message.text:
                context.user_data['game_rating'] = code
                break
        game = Game(id=context.user_data['game_id'], rating=context.user_data['game_rating'])
        username = update.message.from_user.username or 'NOT SET'
        repo: AbstractUserRepository = Container.resolve(AbstractUserRepository)
        user = User(
            id=update.message.from_user.id,
            games=[game],
            username=username,
        )
        await repo.add(user)
        await update.message.reply_text(
            'Дякую, що надав важливу інформацію!\n'
            'Тепер ми зможеш підібрати накращих тімейтів для тебе!\n'
            f'{user}',
        )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls, command: str) -> ConversationHandler:
        entry_point = [CommandHandler(command, cls.start_conversation)]
        states = {
            cls.Handlers.game: [
                MessageHandler(
                    ListFilter(items=[g.name for g in games()]), cls.game_handler
                ),
            ],
            cls.Handlers.rating: [
                MessageHandler(
                    GameRanksFilter(), cls.rating_handler
                ),
            ],
        }
        fallbacks = [CommandHandler('cancel', cls.cancel_command)]
        handler = ConversationHandler(
            entry_points=entry_point,
            states=states,
            fallbacks=fallbacks
        )
        return handler


class CreateTeamConversation(BaseConversationHandler):

    class Handlers(int, Enum):
        start_conversation = 0
        game = 1
        rating = 2
        team_size = 3
        link = 4

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['team'] = {}
        user: User | int = await get_user_or_end_conversation(update, context)
        if isinstance(user, int):
            return user

        choices: list[list[str]] = [[g.name for g in games()]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder='Гра',
        )
        await update.message.reply_text(
            'Для якої гри ти хочеш зробити команду?',
            reply_markup=buttons,
        )
        return cls.Handlers.game

    @classmethod
    async def game_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        game: AbstractGame = get_game_by_name(update.message.text)
        context.user_data['team']['game_id'] = game.id
        choices: list[list[str]] = [[k for k in game.ranks().values()]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text('На якому рівні ти граєш?', reply_markup=buttons)

        return cls.Handlers.rating

    @classmethod
    async def rating_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        for code, value in get_game_by_id(context.user_data['team']['game_id']).ranks().items():
            if value == update.message.text:
                context.user_data['team']['game_rating_value'] = value
                context.user_data['team']['game_rating'] = code
                break
        await update.message.reply_text(
            'Тепер скажи який буде розмір команди? [2-5]'.format(),
        )
        return cls.Handlers.team_size

    @classmethod
    async def team_size_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['team']['size'] = int(update.message.text)
        await update.message.reply_text(
            'Чудово! Тепер створи групу зі своєю назвою та описом '
            'коли закінчиш надішли мені посилання на неї, '
            'Я додам цю групу до пошукової дошки і другі '
            'люди зможуть зайти щоб пограти разом з тобою',
        )
        return cls.Handlers.link

    @classmethod
    async def link_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        group_link = update.message.text
        group_title, group_description = await parse_telegram_webpage(group_link)
        team = Team(
            id=group_link,
            owner_id=context._user_id,
            title=group_title,
            description=group_description if group_description else '',
            size=context.user_data['team']['size'],
            game_id=context.user_data['team']['game_id'],
            game_rating=context.user_data['team']['game_rating'],
        )
        repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
        await repo.add(team)
        response = TeamInfoTextHTML(
            url=group_link,
            title=group_title,
            game=get_game_by_id(team.game_id).name,
            skill=context.user_data['team']['game_rating_value'],
            team_size=team.size,
            description=team.description,
        )
        await update.message.reply_text(
            str(response),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls, command: str) -> ConversationHandler:
        entry_point = [CommandHandler(command, cls.start_conversation)]
        states = {
            cls.Handlers.game: [
                MessageHandler(
                    ListFilter(items=[g.name for g in games()]), cls.game_handler
                ),
            ],
            cls.Handlers.rating: [
                MessageHandler(GameRanksFilter(), cls.rating_handler),
            ],
            cls.Handlers.team_size: [
                MessageHandler(
                    ListFilter(items=['2', '3', '4', '5']),
                    cls.team_size_handler,
                ),
            ],
            cls.Handlers.link: [
                MessageHandler(
                    filters.Regex(r'https:\/\/t\.me\/\+\S+'),
                    cls.link_handler,
                ),
            ]
        }
        fallbacks = [CommandHandler('cancel', cls.cancel_command)]
        handler = ConversationHandler(
            entry_points=entry_point,
            states=states,
            fallbacks=fallbacks
        )
        return handler
