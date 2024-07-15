# type: ignore
from enum import Enum

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from src.common.di import Container
from src.common.config import get_conf
from src.domain.entities import User, Group
from src.common.constants import Game

from src.infra.repositories.base import AbstractUserRepository, AbstractTeamRepository
from src.bot.filters import ListFilter
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

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        choices: list[list[str]] = [[Game.as_string(game.value) for game in Game]]
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
        context.user_data['game'] = Game.from_string(update.message.text)

        username = update.message.from_user.username or 'NOT SET'
        repo: AbstractUserRepository = Container.resolve(AbstractUserRepository)
        user = User(
            id=update.message.from_user.id,
            game=context.user_data['game'],
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
    def get_handler(cls) -> ConversationHandler:
        entry_point = [CommandHandler('profile', cls.start_conversation)]
        states = {
            cls.Handlers.game: [
                MessageHandler(
                    ListFilter(items=[Game.as_string(g.value) for g in Game]), cls.game_handler
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
        team_size = 2
        link = 4

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user: User | int = await get_user_or_end_conversation(update, context)

        if isinstance(user, int):
            return user
        choices: list[list[str]] = [[Game.as_string(g.value) for g in Game]]
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
        context.user_data['game'] = Game.from_string(update.message.text)

        await update.message.reply_text(
            'Тепер скажи який буде розмір команди? [2-5]',
        )
        return cls.Handlers.team_size

    @classmethod
    async def team_size_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['size'] = int(update.message.text)

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
        group = Group(
            id=group_link,
            owner_id=context._user_id,
            title=group_title,
            description=group_description if group_description else '',
            size=context.user_data['size'],
            game=context.user_data['game'],
        )
        repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
        await repo.add(group)
        await update.message.reply_text(
            'Чудово! Тепер твоя група доступна '
            f'для вступу для інших користувачів на {get_conf().REDIS_OBJECTS_LIFETIME // 60} хвилин'
            f'\n{group}'
        )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls) -> ConversationHandler:
        entry_point = [CommandHandler('create', cls.start_conversation)]
        states = {
            cls.Handlers.game: [
                MessageHandler(
                    ListFilter(items=[Game.as_string(g.value) for g in Game]), cls.game_handler
                ),
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
