# type: ignore
from enum import Enum

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from src.common.di import Container
from src.common.config import get_conf
from src.common.entities import User, Group
from src.common.constants import Game, Language
from src.common.filters import GroupFilters, Pagination

from src.infra.repositories.base import AbstractUserRepository, AbstractGroupRepository
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
        language = 2

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        choices: list[list[str]] = [[Game.as_string(game.value) for game in Game]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            one_time_keyboard=True,
            input_field_placeholder='Game',
        )
        await update.message.reply_text(
            'Okay, now I need to get some informaion about you to find the best teammates for you\n'
            'What games do you play from the list?',
            reply_markup=buttons,
        )
        return cls.Handlers.game

    @classmethod
    async def game_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['game'] = Game.from_string(update.message.text)

        choices: list[list[str]] = [[Language.as_string(lan.value) for lan in Language]]
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
        context.user_data['language'] = Language.from_string(update.message.text)

        username = update.message.from_user.username or 'NOT SET'
        repo: AbstractUserRepository = Container.resolve(AbstractUserRepository)
        user = User(
            id=update.message.from_user.id,
            game=context.user_data['game'],
            language=context.user_data['language'],
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
                MessageHandler(
                    ListFilter(items=[Game.as_string(g.value) for g in Game]), cls.game_handler
                ),
            ],
            cls.Handlers.language: [MessageHandler(
                ListFilter(items=[
                    Language.as_string(x.value) for x in Language]), cls.language_handler
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
    # User creates channel and gives channel's id to the bot
    # bot says: okay bro, i'll try to find you some teammates!
    # bot starts to send link to the channel and channel's title
    # to the users which are the best match for the creator of the channel
    # TODO: create flexible grade system for each game

    class Handlers(int, Enum):
        start_conversation = 0
        game = 1
        team_size = 2
        language = 3
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
            input_field_placeholder='Game',
        )
        await update.message.reply_text(
            'For which game you want to create a team?',
            reply_markup=buttons,
        )
        return cls.Handlers.game

    @classmethod
    async def game_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['game'] = Game.from_string(update.message.text)

        await update.message.reply_text(
            'Now, set size of the team [2-5]',
        )
        return cls.Handlers.team_size

    @classmethod
    async def team_size_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['size'] = int(update.message.text)

        choices: list[list[str]] = [[Language.as_string(lan.value) for lan in Language]]
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
        context.user_data['language'] = Language.from_string(update.message.text)

        await update.message.reply_text(
            'Well done! Now you need to create a group with title and description if you want'
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
            size=context.user_data['size'],
            game=context.user_data['game'],
            language=context.user_data['language'],
        )
        repo: AbstractGroupRepository = Container.resolve(AbstractGroupRepository)
        await repo.add(group)
        await update.message.reply_text(
            'Great! Now your group will be available '
            f'for join for the other users for {get_conf().REDIS_OBJECTS_LIFETIME // 60} minutes'
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
            cls.Handlers.language: [MessageHandler(
                ListFilter(
                    items=[Language.as_string(lan.value) for lan in Language]), cls.language_handler
                ),
            ],
            cls.Handlers.link: [
                MessageHandler(
                    filters.Regex(r'https:\/\/t\.me\/\+[A-Za-z0-9]+'),
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


class FindTeamByProfileConversation(BaseConversationHandler):

    class Handlers(int, Enum):
        start_conversation = 0
        find_team = 1

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = await get_user_or_end_conversation(update, context)
        if isinstance(user, int):
            return user
        await update.message.reply_text(
            'I will find you a team according to your profile:\n'
            f'Language: {Language.as_string(user.language)}\n'
            f'Game: {Game.as_string(user.game)}\n'
            'Wait a couple of minutes...',
        )
        return cls.Handlers.find_team

    @classmethod
    async def find_team_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user: User = context.user_data['user']
        filters = GroupFilters(
            game=user.game,
            language=user.language,
        )
        repo: AbstractGroupRepository = Container.resolve(AbstractGroupRepository)
        groups = await repo.search(filters=filters, pag=Pagination(0, 20))
        if groups:
            group_text = '\n'.join(str(group) for group in groups)
            await update.message.reply_text(
                'Here are the available teams to join:\n'
                f'{group_text}'
            )
        else:
            await update.message.reply_text(
                'No available teams found matching your profile.'
                f'{filters}\n'
            )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls) -> ConversationHandler:
        entry_point = [CommandHandler('find', cls.start_conversation)]
        states = {
            cls.Handlers.find_team: [
                MessageHandler(filters.ALL, cls.find_team_handler),
            ],
        }
        fallbacks = [CommandHandler('cancel', cls.cancel_command)]
        handler = ConversationHandler(
            entry_points=entry_point,
            states=states,
            fallbacks=fallbacks
        )
        return handler
