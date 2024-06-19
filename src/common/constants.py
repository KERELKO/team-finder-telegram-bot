from enum import Enum


class Games(str, Enum):
    CS2: str = 'Counter Strike 2'
    AOE2: str = 'Age of empires 2'


class Languages(str, Enum):
    en: str = 'English'
    ukr: str = 'Ukrainian'
