# type: ignore
from enum import Enum
from typing import Callable

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from src.common.di import Container
from src.infra.repositories.base import AbstractUserRepository, AbstractGroupRepository
from src.common.entities import User, Group
from src.common.constants import Games, Languages
from src.bot.filters import ListFilter
from src.bot.utils.parsers import parse_telegram_webpage
from src.bot.utils import get_user_or_end_conversation
from src.common.config import get_conf

from .base import BaseConversationHandler


class CollectUserDataHandler(BaseConversationHandler):
    """
    ### Aggregate handlers into ConversationHandler
    Collect -> Game -> Language -> Skill
    """

    class Handlers(int, Enum):
        start_conversation: int = 0
        game: int = 1
        language: int = 2

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        choices: list[list[str]] = [[game for game in Games]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            one_time_keyboard=True,
            input_field_placeholder='Games',
        )
        await update.message.reply_text(
            'Okay, now I need to get some informaion about you to find the best teammates for you\n'
            'What games do you play from the list?',
            reply_markup=buttons,
        )
        return cls.Handlers.game

    @classmethod
    async def game_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['game'] = update.message.text

        choices: list[list[str]] = [[lan for lan in Languages]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            one_time_keyboard=True,
            input_field_placeholder='Language',
        )
        await update.message.reply_text(
            'Now, tell me on which language you speak the most?',
            reply_markup=buttons,
        )
        return cls.Handlers.language

    @classmethod
    async def language_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['language'] = update.message.text

        username = update.message.from_user.username or 'NOT SET'
        repo: AbstractUserRepository = Container.resolve(AbstractUserRepository)
        user = User(
            id=update.message.from_user.id,
            games=[context.user_data['game']],
            languages=[context.user_data['language']],
            username=username,
        )
        await repo.add(user)
        await update.message.reply_text(
            'Thank for providing your information\n'
            'Now we can find you the best teammates!\n'
            f'{user}',
        )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls) -> ConversationHandler:
        entry_point = [CommandHandler('profile', cls.start_conversation)]
        states = {
            cls.Handlers.game: [
                MessageHandler(ListFilter(items=[x for x in Games]), cls.game_handler),
            ],
            cls.Handlers.language: [MessageHandler(
                ListFilter(items=[x for x in Languages]), cls.language_handler),
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
    # User creates channel and gives channel's id to the bot
    # bot says: okay bro, i'll try to find you some teammates!
    # bot starts to send link to the channel and channel's title
    # to the users which are the best match for the creator of the channel
    # TODO: create flexible grade system for each game

    class Handlers(int, Enum):
        start_conversation: int = 0
        game: int = 1
        team_size: int = 2
        language: int = 3
        link: int = 4

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user: User | int = await get_user_or_end_conversation(update, context)

        if isinstance(user, int):
            return user
        choices: list[list[str]] = [[Games.AOE2, Games.CS2]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder='Game',
        )
        await update.message.reply_text(
            'For which game you want to create a team?',
            reply_markup=buttons,
        )
        return cls.Handlers.game

    @classmethod
    async def game_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['game'] = update.message.text

        await update.message.reply_text(
            'Now, set size of the team [2-5]',
        )
        return cls.Handlers.team_size

    @classmethod
    async def team_size_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['team_size'] = update.message.text

        choices: list[list[str]] = [[lan for lan in Languages]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            one_time_keyboard=True,
            input_field_placeholder='Language',
        )
        await update.message.reply_text(
            'Now, tell me on which language you speak the most?',
            reply_markup=buttons,
        )
        return cls.Handlers.language

    @classmethod
    async def language_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['language'] = update.message.text

        await update.message.reply_text(
            'Well done! Now you need to create group with own title, '
            'when you finish send me link to that group, '
            'I will add this group to a search board and other users will be able to join',
        )
        return cls.Handlers.link

    @classmethod
    async def link_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        group_link = update.message.text
        group_title, group_description = await parse_telegram_webpage(group_link)
        group = Group(
            owner_id=context._user_id,
            title=group_title,
            description=group_description if group_description else '',
            group_size=context.user_data['team_size'],
            game=context.user_data['game'],
            language=context.user_data['language'],
        )
        repo: AbstractGroupRepository = Container.resolve(AbstractGroupRepository)
        await repo.add(group)
        await update.message.reply_text(
            'Great! Now your group will be available '
            f'for join for the other users for {get_conf().REDIS_OBJECTS_LIFETIME / 60} minutes'
            f'\n{group}'
        )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls) -> ConversationHandler:
        entry_point = [CommandHandler('create', cls.start_conversation)]
        states = {
            cls.Handlers.game: [
                MessageHandler(ListFilter(items=[x for x in Games]), cls.game_handler),
            ],
            cls.Handlers.team_size: [
                MessageHandler(
                    ListFilter(items=['2', '3', '4', '5']),
                    cls.team_size_handler,
                ),
            ],
            cls.Handlers.language: [MessageHandler(
                ListFilter(items=[x for x in Languages]), cls.language_handler),
            ],
            cls.Handlers.link: {
                MessageHandler(
                    filters.Regex(r'https:\/\/t\.me\/\+[A-Za-z0-9]+'),
                    cls.link_handler,
                ),
            }
        }
        fallbacks = [CommandHandler('cancel', cls.cancel_command)]
        handler = ConversationHandler(
            entry_points=entry_point,
            states=states,
            fallbacks=fallbacks
        )
        return handler


class FindTeamConversation(BaseConversationHandler):
    class Handlers(int, Enum):
        start_conversation: int = 0
        action: int = 1
        list_groups: int = 2
        find_team: int = 3

    class Actions(str, Enum):
        list_groups: str = 'I want to see list of available groups'
        search: str = 'Search a team for me'

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        choices: list[list[str]] = [[game for game in Games]]
        buttons = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=choices,
            one_time_keyboard=True,
            input_field_placeholder='Game',
        )
        await update.message.reply_text(
            'Lets find you a team',
            reply_markup=buttons,
        )
        return cls.Handlers.action

    @classmethod
    async def action_handler(
        cls, update: Update, context: ContextTypes.DEFAULT_TYPE,
    ) -> int | Callable:
        context.user_data['selected_game'] = update.message.text

        choices: list[list[str]] = [[x for x in cls.Actions]]
        buttons = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=choices,
            one_time_keyboard=True,
            input_field_placeholder='Action',
        )
        message = await update.message.reply_text(
            text='Now, choose what to do next',
            reply_markup=buttons,
        )
        if message.text == cls.Actions.search:
            return cls.Handlers.find_team
        elif message.text == cls.Actions.list_groups:
            return cls.Handlers.list_groups
        return cls.action_handler(cls, update=update, context=context)

    @classmethod
    async def list_groups_handler(
        cls, update: Update, context: ContextTypes.DEFAULT_TYPE,
    ) -> list[tuple[int, str]]:
        ...

    @classmethod
    async def find_team_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ...
