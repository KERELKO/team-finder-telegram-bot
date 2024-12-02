from dataclasses import dataclass
from enum import StrEnum

from src.common.config import get_conf
from src.domain.entities.games.base import GameData
from src.common.utils import get_game_by_id, get_game_rank_value


class BotCommand(StrEnum):
    START = 'start'
    HELP = 'help'
    FIND_TEAM = 'find_team'
    CREATE_PROFILE = 'create_profile'
    CREATE_TEAM = 'create_team'
    UPDATE_TEAM = 'update_team'


_START_TEXT = """
Привіт! Я — TeamFinderBot 🤖\n
Моя місія — допомогти тобі знайти команду для улюблених ігор 🎮\n
Спробуй команду /{0}, щоб дізнатися більше про мої можливості!
"""
START_TEXT = _START_TEXT.format(BotCommand.HELP)

_HELP_TEXT = """
Допоміжний текст, використаний командою /{0}\n
Почати /{1} команда\n
/{2} - створити базовий профіль🎀\n
/{3} - знайти команду згідно профілю🔎\n
/{4} - створити команду🪄\n
/{5} - змінити налаштування створеної команди📝\n
"""
HELP_TEXT = _HELP_TEXT.format(
    BotCommand.HELP,
    BotCommand.START,
    BotCommand.CREATE_PROFILE,
    BotCommand.FIND_TEAM,
    BotCommand.CREATE_TEAM,
    BotCommand.UPDATE_TEAM,
)


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
    description: str | None = None
    preface: str | None = None

    def __str__(self) -> str:
        minutes: int = get_conf().REDIS_OBJECTS_LIFETIME // 60
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
    show_id: bool = False

    def __str__(self) -> str:
        text = _USER_INFO_TEXT_HTML
        id_text = ''
        if self.show_id:
            id_text = f'👤<u><b>ID:</b></u> {self.id}'
        games = []
        for game_data in self.games:
            game = get_game_by_id(game_data.id)
            if not game:
                continue
            games.append(f'\t<b>{game.name} [{get_game_rank_value(game, game_data.rating)}]</b>')

        return text.format(self.username, id_text, '\n'.join(games) if games else '')
