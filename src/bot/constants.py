from dataclasses import dataclass

from src.common.config import get_conf


START_TEXT = """
Привіт від TeamFinderBot!\n
Я спробую допомогти знайти тобі команду для певних ігор\n
можеш використати команду /help яка допоможе розбіратись в функціоналі
"""

HELP_TEXT = """
Допоміжний текст, використаний командою /help\n
Почати /start команда\n
/profile - щоб створити базовий профіль\n
/find - щоб знайти команду згідно профілю\n
/create - щоб створити команду\n
"""

_TEAM_INFO_TEXT_HTML = """
{0}
<u><b>Посилання:</b></u> {1}
<u><b>Заголовок:</b></u> {2}
<u><b>Гра:</b></u> {3}
<u><b>Скіл:</b></u> {4}
<u><b>Розмір команди:</b></u> {5}
{6}
"""


@dataclass(eq=False, repr=False)
class TeamInfoTextHTML:
    """Formats base team info text with given params, use `__str__` to get formatted text"""
    url: str
    title: str
    game: str
    skill: str
    team_size: int
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
            preface, self.url, self.title, self.game, self.skill, self.team_size, desc_text
        )
