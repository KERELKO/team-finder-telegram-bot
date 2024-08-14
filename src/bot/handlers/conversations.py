# type: ignore
import asyncio
from enum import Enum

from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from src.common.di import Container
from src.common.utils import get_game_by_id, get_game_by_name
from src.domain.entities.games.base import AbstractGame, AbstractGames, GameData
from src.domain.entities import User, Team
from src.infra.repositories.base import AbstractUserRepository, AbstractTeamRepository

from src.bot.constants import TeamInfoTextHTML, BotCommands, UserInfoTextHTML
from src.bot.filters import ListFilter, GameRanksFilter
from src.bot.utils.parsers import parse_telegram_webpage
from src.bot.utils import get_user_or_end_conversation

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
        games: AbstractGames = Container.resolve(AbstractGames)
        choices: list[list[str]] = [[game.name for game in games]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            one_time_keyboard=True,
            input_field_placeholder='Гра',
        )
        await update.message.reply_text(
            'Зараз мені потрібно дізнатись більше про тебе, скажи в які гру зі списку ти граєш?',
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
            'Дякую, що надав важливу інформацію!\n'
            'Тепер я зможу підібрати накращих тімейтів для тебе!\n'
            f'{str(reply_text)}',
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls, command: str) -> ConversationHandler:
        entry_point = [CommandHandler(command, cls.start_conversation)]
        games: AbstractGames = Container.resolve(AbstractGames)
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
            await update.message.reply_text(
                'Не можна створювати команду якщо вже є активна\n'
                'якщо хочеш створити нову команду видали минулу\n'
                f'допоміжна команда: /{BotCommands.UPDATE_TEAM}'
            )
            return
        games: AbstractGames = Container.resolve(AbstractGames)
        choices: list[list[str]] = [[g.name for g in games]]
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
            'Скільки гравців тобі потрібно? [1-5]',
        )
        return cls.Handlers.team_size

    @classmethod
    async def team_size_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['team']['players_to_fill'] = int(update.message.text)
        await update.message.reply_text(
            'Чудово! Тепер створи групу зі своєю назвою та описом '
            'коли закінчиш надішли мені посилання на неї, '
            'я додам цю групу до пошукової дошки і другі '
            'користувачі зможуть зайти щоб пограти разом з тобою',
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
        games: AbstractGames = Container.resolve(AbstractGames)
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

    end_search = 'Закрити пошук команди'
    update_players = 'Змінити потрібну кількість учасників'

    class Handlers(int, Enum):
        start_conversation = 0
        end_search_or_next = 1
        number_of_players = 3

    @classmethod
    async def start_conversation(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = await get_user_or_end_conversation(update, context)
        if user is ConversationHandler.END:
            return ConversationHandler.END
        repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
        team = await repo.get_by_owner_id(user.id)
        if not team:
            await update.message.reply_text(
                'Команд по твому профілю не знайдено'
            )
            return ConversationHandler.END
        context.user_data['team'] = team

        choices = [[cls.end_search, cls.update_players]]
        buttons = ReplyKeyboardMarkup(
            keyboard=choices,
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text(
            'Виберіть дію',
            reply_markup=buttons,
        )
        return cls.Handlers.end_search_or_next

    @classmethod
    async def path_handler(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        choice = update.message.text
        if choice == cls.update_players:
            await update.message.reply_text(
                'Скільки ще потрібно гравців щоб створити повну команду? [0-5]'
            )
            return cls.Handlers.number_of_players
        elif choice == cls.end_search:
            repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
            await repo.delete_by_owner_id(context._user_id)
            await update.message.reply_text('Команда була видалена з пошуку успішно!')
        return ConversationHandler.END

    @classmethod
    async def change_number_of_players_handlers(
        cls, update: Update, context: ContextTypes.DEFAULT_TYPE,
    ) -> int:
        count = int(update.message.text)
        repo: AbstractTeamRepository = Container.resolve(AbstractTeamRepository)
        if count == 0:
            await repo.delete_by_owner_id(context._user_id)
            await update.message.reply_text(
                'Потрібна кількість користувачів для команди знайдена\n'
                'Закриваю пошук...'
            )
            await asyncio.sleep(1)
            await update.message.reply_text(
                'Команда була видалена з пошуку успішно!'
            )
            return ConversationHandler.END
        await repo.update_players_count(context.user_data['team'].id, count)
        await update.message.reply_text(
            'Успішно обновлено!'
        )
        return ConversationHandler.END

    @classmethod
    def get_handler(cls, command: str) -> ConversationHandler:
        entry_point = [CommandHandler(command, cls.start_conversation)]
        states = {
            cls.Handlers.number_of_players: [
                MessageHandler(
                    ListFilter(items=[cls.end_search, cls.update_players]), cls.path_handler
                ),
            ],
            cls.Handlers.end_search_or_next: [
                MessageHandler(
                    filters.ALL, cls.path_handler
                ),
            ],
            cls.Handlers.number_of_players: [
                MessageHandler(
                    ListFilter(items=['0', '1', '2', '3', '4', '5']),
                    cls.change_number_of_players_handlers,
                ),
            ],
        }
        fallbacks = [
            CommandHandler('cancel', cls.cancel_command),
            CommandHandler('2', cls.cancel_command),
        ]
        handler = ConversationHandler(
            entry_points=entry_point,
            states=states,
            fallbacks=fallbacks
        )
        return handler
