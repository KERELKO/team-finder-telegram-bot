from enum import Enum


class Game(int, Enum):
    CS2 = 1
    AOE2 = 2

    @staticmethod
    def as_string(code: int) -> str:
        return Game.dictionary()[code]

    @staticmethod
    def from_string(string: str) -> int | None:
        for key, value in Game.dictionary().items():
            if value == string:
                return key

    @staticmethod
    def dictionary() -> dict[int, str]:
        return {
            1: 'Counter Strike 2',
            2: 'Age of Empires 2',
        }


class Language(int, Enum):
    en = 1
    ukr = 2

    @staticmethod
    def dictionary() -> dict[int, str]:
        return {
            1: 'English',
            2: 'Ukrainian',
        }

    @staticmethod
    def from_string(string: str) -> int | None:
        for key, value in Language.dictionary().items():
            if value == string:
                return key

    @staticmethod
    def as_string(code: int) -> str:
        return Language.dictionary()[code]
