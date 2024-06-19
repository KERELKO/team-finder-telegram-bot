# type: ignore
from enum import Enum
from typing import Callable

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, filters, MessageHandler

from src.common.dtos import UserDTO
from src.common.constants import Games, Languages
from src.bot.filters import ListFilter

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
        skill: int = 3

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

        await update.message.reply_text(
            'Excelent!\n'
            'And the last question, how you rate yourself in this game from 1 to 10?',
        )
        return cls.Handlers.skill

    @staticmethod
    async def skill_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['skill'] = update.message.text
        await update.message.reply_text(
            'Thank for providing your information\n'
            'Now we can find you the best teammates!\n'
        )
        username = update.message.from_user.username or 'NOT SET'
        user = UserDTO(
            id=update.message.from_user.id,
            game=context.user_data['game'],
            username=username,
            skill=context.user_data['skill'],
            language=context.user_data['language'],
        )
        print(user)
        return ConversationHandler.END

    @classmethod
    def get_handler(cls) -> ConversationHandler:
        entry_point = [CommandHandler('collect', cls.start_conversation)]
        states = {
            cls.Handlers.game: [
                MessageHandler(ListFilter(items=[x for x in Games]), cls.game_handler)
            ],
            cls.Handlers.language: [MessageHandler(
                ListFilter(items=[x for x in Languages]), cls.language_handler),
            ],
            cls.Handlers.skill: [
                MessageHandler(filters.Regex('^[1-9]$|^10$'), cls.skill_handler)
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
        context.user_data['game_for_group'] = update.message.text
        return cls.Handlers.create_group

    @classmethod
    async def create_group_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return ConversationHandler.END


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
