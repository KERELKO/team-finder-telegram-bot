# type: ignore
import asyncio
from enum import Enum

from telegram import ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.constants import (
    CHOOSE_GAME_FROM_THE_LIST_TEXT,
    HOW_GOOD_YOU_ARE_TEXT,
    HOW_MANY_PLAYERS_DO_YOU_NEED_TEXT,
    AFTER_CREATED_PROFILE_TEXT,
    TeamInfoTextHTML,
    UPDATED_TEXT,
    TEAM_ALREADY_ACTIVE_TEXT,
    PROFILE_FOR_GAME_TEXT,
    FAILED_TO_FIND_TEAM_BY_PROFILE,
    PLAYERS_TO_FILL_TEXT,
    UserInfoTextHTML,
    END_SERCH_TEXT,
    UPDATE_PLAYERS_COUNT_TEXT,
    TEAM_WAS_SUCCESSFULLY_DELETED_TEXT,
    GET_TELEGRAM_GROUP_LINK_AND_FINISH_TEAM_CREATION_TEXT,
)
from src.bot.filters import GameRanksFilter, ListFilter
from src.bot.utils import get_user_or_end_conversation
from src.bot.utils.parsers import parse_telegram_webpage
from src.common.di import Container
from src.common.utils import get_game_by_id, get_game_by_name
from src.domain.entities.games.base import AbstractGame, GameData, Games
from src.domain.entities.users import Team, User
from src.infra.repositories.base import AbstractTeamRepository, AbstractUserRepository

from .base import BaseConversationHandler


class CollectUserDataConversation(BaseConversationHandler):
    """
    ### Aggregate handlers into ConversationHandler
    Start -> Game -> Rating
    """

    class Handlers(int, Enum):
        start_conversation = 0
        game = 1
        rating = 2

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        games: Games = Container.resolve(Games)
        choices: list[list[str]] = [[game.name for game in games]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            one_time_keyboard=True,
            input_field_placeholder='Гра',
        )
        await update.message.reply_text(CHOOSE_GAME_FROM_THE_LIST_TEXT, reply_markup=buttons)
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
            HOW_GOOD_YOU_ARE_TEXT,
            reply_markup=buttons,
        )
        return cls.Handlers.rating

    @classmethod
    async def rating_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        for code, value in get_game_by_id(context.user_data['game_id']).ranks().items():
            if value == update.message.text:
                context.user_data['game_rating'] = code
                break
        game = GameData(id=context.user_data['game_id'], rating=context.user_data['game_rating'])
        username = update.message.from_user.username or 'NOT SET'
        repo: AbstractUserRepository = Container.resolve(AbstractUserRepository)
        user = User(
            id=update.message.from_user.id,
            games=[game],
            username=username,
        )
        await repo.add(user)
        reply_text = UserInfoTextHTML(
            id=user.id,
            username=user.username,
            games=user.games,
            show_id=False
        )
        await update.message.reply_text(
            AFTER_CREATED_PROFILE_TEXT +
            f'{str(reply_text)}',
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls, command: str) -> ConversationHandler:
        entry_point = [CommandHandler(command, cls.start_conversation)]
        games: Games = Container.resolve(Games)
        states = {
            cls.Handlers.game: [
                MessageHandler(
                    ListFilter(items=[g.name for g in games]), cls.game_handler
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
    """
    Start -> Game -> Rating -> Team size -> Link
    """

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
        repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)

        team = await repo.get_by_owner_id(owner_id=user.id)
        if team is not None:
            await update.message.reply_text(TEAM_ALREADY_ACTIVE_TEXT)
            return ConversationHandler.END
        games: Games = Container.resolve(Games)
        choices: list[list[str]] = [[g.name for g in games]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder='Гра',
        )
        await update.message.reply_text(
            PROFILE_FOR_GAME_TEXT,
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
        await update.message.reply_text(HOW_GOOD_YOU_ARE_TEXT, reply_markup=buttons)

        return cls.Handlers.rating

    @classmethod
    async def rating_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        for code, value in get_game_by_id(context.user_data['team']['game_id']).ranks().items():
            if value == update.message.text:
                context.user_data['team']['game_rating_value'] = value
                context.user_data['team']['game_rating'] = code
                break
        await update.message.reply_text(HOW_MANY_PLAYERS_DO_YOU_NEED_TEXT)
        return cls.Handlers.team_size

    @classmethod
    async def team_size_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['team']['players_to_fill'] = int(update.message.text)
        await update.message.reply_text(GET_TELEGRAM_GROUP_LINK_AND_FINISH_TEAM_CREATION_TEXT)
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
            players_to_fill=context.user_data['team']['players_to_fill'],
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
            players_to_fill=team.players_to_fill,
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
        games: Games = Container.resolve(Games)
        states = {
            cls.Handlers.game: [
                MessageHandler(
                    ListFilter(items=[g.name for g in games]), cls.game_handler
                ),
            ],
            cls.Handlers.rating: [
                MessageHandler(GameRanksFilter(), cls.rating_handler),
            ],
            cls.Handlers.team_size: [
                MessageHandler(
                    ListFilter(items=['1', '2', '3', '4', '5']),
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


class UpdateTeamConversation(BaseConversationHandler):
    """
    Update team -> End search | Change needed users count
    """

    class Handlers(int, Enum):
        start_conversation = 0
        end_search_or_continue = 1
        number_of_players = 3

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = await get_user_or_end_conversation(update, context)
        if user is ConversationHandler.END:
            return ConversationHandler.END
        repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
        team = await repo.get_by_owner_id(user.id)
        if not team:
            await update.message.reply_text(FAILED_TO_FIND_TEAM_BY_PROFILE)
            return ConversationHandler.END
        context.user_data['team'] = team

        choices = [[END_SERCH_TEXT, UPDATE_PLAYERS_COUNT_TEXT]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text(
            'Вибери дію',
            reply_markup=buttons,
        )
        return cls.Handlers.end_search_or_continue

    @classmethod
    async def action_with_choice_handler(
        cls, update: Update, context: ContextTypes.DEFAULT_TYPE,
    ) -> int:
        choice = update.message.text
        if choice == UPDATE_PLAYERS_COUNT_TEXT:
            await update.message.reply_text(PLAYERS_TO_FILL_TEXT)
            return cls.Handlers.number_of_players
        elif choice == END_SERCH_TEXT:
            repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
            await repo.delete_by_owner_id(context._user_id)
            await update.message.reply_text(TEAM_WAS_SUCCESSFULLY_DELETED_TEXT)
        return ConversationHandler.END

    @classmethod
    async def change_number_of_players_handlers(
        cls, update: Update, context: ContextTypes.DEFAULT_TYPE,
    ) -> int:
        count = int(update.message.text)
        repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
        if count == 0:
            await repo.delete_by_owner_id(context._user_id)
            await update.message.reply_text(END_SERCH_TEXT)
            await asyncio.sleep(1)
            await update.message.reply_text(TEAM_WAS_SUCCESSFULLY_DELETED_TEXT)
            return ConversationHandler.END
        await repo.update_players_count(context.user_data['team'].id, count)
        await update.message.reply_text(UPDATED_TEXT)
        return ConversationHandler.END

    @classmethod
    def get_handler(cls, command: str) -> ConversationHandler:
        entry_point = [CommandHandler(command, cls.start_conversation)]
        states = {
            cls.Handlers.number_of_players: [
                MessageHandler(
                    ListFilter(
                        items=[END_SERCH_TEXT, UPDATE_PLAYERS_COUNT_TEXT]
                    ),
                    cls.action_with_choice_handler
                ),
            ],
            cls.Handlers.end_search_or_continue: [
                MessageHandler(
                    filters.ALL, cls.action_with_choice_handler
                ),
            ],
            cls.Handlers.number_of_players: [
                MessageHandler(
                    ListFilter(items=['0', '1', '2', '3', '4', '5']),
                    cls.change_number_of_players_handlers,
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
