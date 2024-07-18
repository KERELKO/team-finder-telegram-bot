from dataclasses import dataclass

from src.common.config import get_conf
from src.domain.entities.games import Game


class BotCommands:
    START = 'start'
    HELP = 'help'
    FIND_TEAM = 'find'
    CREATE_PROFILE = 'profile'
    CREATE_TEAM = 'create'
    UPDATE_TEAM = 'update_team'


_START_TEXT = """
Привіт від TeamFinderBot!\n
Я спробую допомогти знайти тобі команду для певних ігор\n
можеш використати команду /{0} яка допоможе розбіратись в функціоналі
"""
START_TEXT = _START_TEXT.format(BotCommands.HELP)

_HELP_TEXT = """
Допоміжний текст, використаний командою /{0}\n
Почати /{1} команда\n
/{2} - створити базовий профіль\n
/{3} - знайти команду згідно профілю\n
/{4} - створити команду\n
"""
HELP_TEXT = _HELP_TEXT.format(
    BotCommands.HELP,
    BotCommands.START,
    BotCommands.CREATE_PROFILE,
    BotCommands.FIND_TEAM,
    BotCommands.CREATE_TEAM,
)

_TEAM_INFO_TEXT_HTML = """
{0}
<u><b>Посилання:</b></u> {1}
<u><b>Заголовок:</b></u> {2}
<u><b>Гра:</b></u> {3}
<u><b>Скіл:</b></u> {4}
<u><b>Гравців потрібно:</b></u> {5}
{6}
"""

_USER_INFO_TEXT_HTML = """
<u><b>Нікнейм:</b></u> {0}
{1}
<u><b>ігри:</b></u> {2}
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
                'Чудово! Тепер твоя група доступна для вступу для інших користувачів'
                f'на <u><b>{minutes_text}</b></u>'
            )

        desc_text = f'<u><b>Опис:</b></u> {self.description}' if self.description else ''

        return text.format(
            preface, self.url, self.title, self.game, self.skill, self.players_to_fill, desc_text
        )


@dataclass
class UserInfoHTML:
    id: int
    username: str
    games: list[Game]
    show_id: bool = False

    def __str__(self) -> str:
        text = _USER_INFO_TEXT_HTML
        id_text = ''
        if self.show_id:
            id_text = f'<u><b>айді:</b></u> {self.id}'
        return text.format(self.username, id_text, )
