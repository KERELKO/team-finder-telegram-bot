import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(repr=False, slots=True, eq=False, frozen=True)
class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', default='')


def get_conf() -> Config:
    return Config()
