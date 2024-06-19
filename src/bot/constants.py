from enum import Enum


START_TEXT = """
   Hi from TeamBot!\n
   I want to help you to find teammates for different games\n
"""

HELP_TEXT = """
    help text, used with /help command
"""


class Games(str, Enum):
    CS2: str = 'Counter Strike 2'
    AOE2: str = 'Age of empires 2'


class Languages(str, Enum):
    en: str = 'English'
    ukr: str = 'Ukrainian'


class CreateTeamEnum(Enum):
    ...


class JoinTeamEnum(Enum):
    ...
