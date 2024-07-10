import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(repr=False, slots=True, eq=False, frozen=True)
class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', default='')
    MONGO_PORT: str = os.getenv('MONGO_PORT', default='27027')
    MONGO_HOST: str = os.getenv('MONGO_HOST', default='mongodb')

    def __post_init__(self) -> None:
        for field in self.__slots__:
            if not getattr(self, field):
                raise AttributeError(f'{field} was not provided in .env file')


def get_conf() -> Config:
    return Config()
