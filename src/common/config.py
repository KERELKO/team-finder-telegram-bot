import os
from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from dotenv import load_dotenv


load_dotenv()


@dataclass(repr=False, slots=True, eq=False, frozen=True)
class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', default='')
    MONGO_PORT: int = int(os.getenv('MONGO_PORT', default='27017'))
    MONGO_HOST: str = os.getenv('MONGO_HOST', default='mongodb')

    REDIS_HOST: str = os.getenv('REDIS_HOST', 'memory')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6379'))

    def __post_init__(self) -> None:
        for field in self.__slots__:
            if not getattr(self, field):
                raise AttributeError(f'{field} was not provided in .env file')

    def get_async_mongo_client(self) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(host=self.MONGO_HOST, port=self.MONGO_PORT)

    def mongodb_user_collection(self) -> AsyncIOMotorCollection:
        return self.get_async_mongo_client()['users_db']['users']


def get_conf() -> Config:
    return Config()
