from enum import Enum


class Games(str, Enum):
    CS2 = 'Counter Strike 2'
    AOE2 = 'Age of empires 2'


class Languages(str, Enum):
    en = 'English'
    ukr = 'Ukrainian'
