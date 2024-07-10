# type: ignore
from enum import Enum
from typing import Callable

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler

from src.infra.managers.base import AbstractGroupManager
from src.common.entities import User, Group
from src.common.constants import Games, Languages
from src.bot.filters import ListFilter
from src.bot.utils.parsers import parse_telegram_webpage

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
        user = User(
            id=update.message.from_user.id,
            games=[context.user_data['game']],
            languages=[context.user_data['language']],
            username=username,
        )
        await update.message.reply_text(
            'Thank for providing your information\n'
            'Now we can find you the best teammates!\n'
            f'{user}',
        )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls) -> ConversationHandler:
        entry_point = [CommandHandler('collect', cls.start_conversation)]
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
    group_manager: AbstractGroupManager

    class Handlers(int, Enum):
        start_conversation: int = 0
        game: int = 1
        create_group: int = 2

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        choices: list[list[str]] = [[Games.AOE2, Games.CS2]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder='Game',
        )
        await update.message.reply_text(
            'For which game you want to create team?',
            reply_markup=buttons,
        )
        return cls.Handlers.game

    @classmethod
    async def game_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['game'] = update.message.text
        # User creates channel and gives channel's id to the bot
        # bot says: okay bro, i'll try to find you some teammates!
        # bot starts to send link to the channel and channel's title
        # to the users which are the best match for the creator of the channel
        # TODO: create flexible grade system for each game
        await update.message.reply_text(
            'Well done! Now you need to create group with own title, '
            'when you finish send me link to that group, '
            'I will add this group to a search and other users will be able to join',
        )
        return cls.Handlers.create_group

    @classmethod
    async def create_group_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        group_link = update.message.text
        group_title, group_description = parse_telegram_webpage(group_link)
        group = Group(
            title=group_title,
            group_size=context.user_data['group_size'],
            game=context.user_data['game'],
            language=Languages.ukr,
        )
        print(group)
        cls.group_manager.add_group(group)
        return ConversationHandler.END

    @classmethod
    def get_handler(cls) -> ConversationHandler:
        ...


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
