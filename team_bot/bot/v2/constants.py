from dataclasses import dataclass
from enum import StrEnum

from team_bot.domain.entities.games.base import GameCollection
from team_bot.domain.entities.users import GameData
from team_bot.domain.utils import get_game_by_id, get_game_rank_value


class BotCommand(StrEnum):
    START = 'start'
    HELP = 'help'
    FIND_TEAM = 'find_team'
    CREATE_PROFILE = 'create_profile'
    CREATE_TEAM = 'create_team'
    UPDATE_TEAM = 'update_team'


CANCEL_TEXT = """Розмова перервана"""

_START_TEXT = """
Привіт! Я — TeamFinderBot 🤖\n
Моя місія — допомогти тобі знайти команду для улюблених ігор 🎮\n
Спробуй команду /{0}, щоб дізнатися більше про мої можливості!
"""
START_TEXT = _START_TEXT.format(BotCommand.HELP)

_HELP_TEXT = """
Допоміжний текст, використаний командою /{0}\n
⛳️/{1} - почати\n
🎀/{2} - створити базовий профіль\n
🔎/{3} - знайти команду згідно профілю\n
🪄/{4} - створити команду\n
📝/{5} - змінити налаштування створеної команди\n
"""
HELP_TEXT = _HELP_TEXT.format(
    BotCommand.HELP,
    BotCommand.START,
    BotCommand.CREATE_PROFILE,
    BotCommand.FIND_TEAM,
    BotCommand.CREATE_TEAM,
    BotCommand.UPDATE_TEAM,
)

_NO_PROFILE_TEXT = """
У тебе ще немає профілю.\n
Використай команду /{0}, щоб створити профіль
"""
NO_PROFILE_TEXT = _NO_PROFILE_TEXT.format(BotCommand.CREATE_PROFILE)

FIND_TEAM_BY_PROFILE_TEXT = """
Спробую знайти команду згідно твого профілю.\n
Зачекай трішки...
"""

NO_AVAILABLE_TEAMS_TEXT = """
Доступних команд для входу поки що немає :(\n
Cпробуй створити свою, може хтось захоче пограти
"""

FAILED_TO_FIND_TEAM_BY_PROFILE = """
Команд по твому профілю не знайдено 😟
"""

GET_TELEGRAM_GROUP_LINK_AND_FINISH_TEAM_CREATION_TEXT = """
Чудово!🥳 Тепер створи групу зі своєю назвою та описом.
Коли закінчиш, надішли мені посилання на неї.
Я додам цю групу до пошукової дошки і другі
користувачі зможуть зайти, щоб пограти разом з тобою
"""

PROFILE_FOR_GAME_TEXT = """
Для якої гри ти хочеш зробити команду?✨
"""

_TEAM_ALREADY_ACTIVE_TEXT = """
Не можна створювати команду, якщо вже є активна ❌\n
Якщо хочеш створити нову команду - видали минулу.\n
Допоміжна команда: /{0}
"""
TEAM_ALREADY_ACTIVE_TEXT = _TEAM_ALREADY_ACTIVE_TEXT.format(BotCommand.UPDATE_TEAM)

AFTER_CREATED_PROFILE_TEXT = """
Дякую за надану інформацію!\n
Тепер я зможу знайти найкращих гравців для твоєї команди!✅
"""

HOW_GOOD_YOU_ARE_TEXT = """
На якому рівні ти граєш?🪖
"""

HOW_MANY_PLAYERS_DO_YOU_NEED_TEXT = """
Скільки гравців тобі потрібно? [1-5]
"""

PLAYERS_TO_FILL_TEXT = """
Скільки ще потрібно гравців, щоб створити повну команду? [0-5]🪤
"""

CHOOSE_GAME_FROM_THE_LIST_TEXT = """
Зараз мені потрібно дізнатися більше про тебе. Скажи, у яку гру зі списку ти граєш?🌝
"""

TEAM_WAS_SUCCESSFULLY_DELETED_TEXT = """
Команда була видалена з пошуку успішно!✅
"""

UPDATED_TEXT = """Успішно оновлено!✅"""

END_SERCH_TEXT = 'Закрити пошук команди🔒'
UPDATE_PLAYERS_COUNT_TEXT = 'Змінити потрібну кількість учасників📝'

_TEAM_INFO_TEXT_HTML = """
{0}
⛓<u><b>Посилання:</b></u> {1}\n
✏️<u><b>Заголовок:</b></u> {2}\n
⚔️<u><b>Гра:</b></u> {3}\n
🎖<u><b>Скіл:</b></u> {4}\n
👥<u><b>Гравців потрібно:</b></u> {5}\n
{6}
"""


@dataclass(eq=False, repr=False)
class TeamInfoTextHTML:
    """Formats base team info text with given params, use `__str__` to get formatted text"""
    url: str
    title: str
    game: str
    skill: str
    players_to_fill: int
    team_ttl: int
    description: str | None = None
    preface: str | None = None

    def __str__(self) -> str:
        minutes: int = self.team_ttl // 60
        text = _TEAM_INFO_TEXT_HTML
        if minutes == 1:
            minutes_text = f'{minutes} хвилину'
        elif minutes in [2, 3, 4]:
            minutes_text = f'{minutes} хвилини'
        else:
            minutes_text = f'{minutes} хвилин'
        if self.preface is not None:
            preface = self.preface
        else:
            preface = (
                '🏆Чудово! Тепер твоя група доступна для вступу для інших користувачів '
                f'на <u><b>{minutes_text}</b></u>\n'
            )

        desc_text = f'📖<u><b>Опис:</b></u> {self.description}' if self.description else ''

        return text.format(
            preface, self.url, self.title, self.game, self.skill, self.players_to_fill, desc_text
        )


_USER_INFO_TEXT_HTML = """
👤<u><b>Нікнейм:</b></u> {0}
{1}
⚔️<u><b>Ігри:</b></u>
{2}
"""


@dataclass(repr=False, eq=False)
class UserInfoTextHTML:
    id: int
    username: str
    games: list[GameData]
    game_collection: GameCollection
    show_id: bool = False

    def __str__(self) -> str:
        text = _USER_INFO_TEXT_HTML
        id_text = ''
        if self.show_id:
            id_text = f'👤<u><b>ID:</b></u> {self.id}'
        games = []
        for game_data in self.games:
            game = get_game_by_id(game_data.id, self.game_collection)
            if not game:
                continue
            games.append(f'\t<b>{game.name} [{get_game_rank_value(game, game_data.rating)}]</b>')

        return text.format(self.username, id_text, '\n'.join(games) if games else '')
