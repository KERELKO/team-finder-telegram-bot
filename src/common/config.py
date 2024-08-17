import os
from pathlib import Path
from functools import cache
from dataclasses import dataclass, field

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

import redis
import redis.asyncio as aioredis
from redis.commands.search.field import NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

from dotenv import load_dotenv


load_dotenv()


@dataclass(repr=False, slots=True, eq=False, frozen=True)
class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', default='')
    MONGO_PORT: int = int(os.getenv('MONGO_PORT', default='27017'))
    MONGO_HOST: str = os.getenv('MONGO_HOST', default='mongodb')

    REDIS_HOST: str = os.getenv('REDIS_HOST', default='memory')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', default='6379'))

    REDIS_OBJECTS_LIFETIME: int = 15 * 60

    RATING_OFFSET: int = 1

    def __post_init__(self) -> None:
        for _field in self.__slots__:
            if not getattr(self, _field):
                raise AttributeError(f'{_field} was not provided in .env file')

    @property
    def games_json_path(self) -> str:
        root = Path(__file__).resolve().parent.parent.parent
        return str(root) + '/games.json'

    @property
    def redis_url(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    def get_async_mongo_client(self) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(host=self.MONGO_HOST, port=self.MONGO_PORT)

    def mongodb_user_collection(self) -> AsyncIOMotorCollection:
        return self.get_async_mongo_client()['users_db']['users']


@dataclass(repr=False, slots=True, eq=False, frozen=True)
class RedisConfig:
    TEAM_SCHEMA: tuple = field(default=(
            NumericField(name='$.owner_id', as_name='owner_id'),
            NumericField(name='$.game_id', as_name='game_id'),
            NumericField(name='$.game_rating', as_name='game_rating'),
        ),
        kw_only=True,
    )

    TEAM_INDEX_NAME: str = 'idx:teams'
    TEAM_INDEX_PREFIX: str = 'team:'

    @staticmethod
    async def get_async_redis_client() -> aioredis.Redis:
        config = get_conf()
        return await aioredis.from_url(config.redis_url)

    def create_team_index(self) -> bool:
        config = get_conf()
        r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

        indexes = r.execute_command('FT._LIST')
        if self.TEAM_INDEX_NAME.encode() in indexes:
            return False

        rs = r.ft(self.TEAM_INDEX_NAME)
        rs.create_index(
            self.TEAM_SCHEMA,
            definition=IndexDefinition(
                prefix=[self.TEAM_INDEX_PREFIX], index_type=IndexType.JSON
            )
        )
        return True


@cache
def get_conf() -> Config:
    return Config()


@cache
def get_redis_conf() -> RedisConfig:
    return RedisConfig()
