from functools import cache
import os
from dataclasses import dataclass, field

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

import redis
import redis.asyncio as aioredis
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

from dotenv import load_dotenv


load_dotenv()


@dataclass(repr=False, slots=True, eq=False, frozen=True)
class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', default='')
    MONGO_PORT: int = int(os.getenv('MONGO_PORT', default='27017'))
    MONGO_HOST: str = os.getenv('MONGO_HOST', default='mongodb')

    REDIS_HOST: str = os.getenv('REDIS_HOST', 'memory')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', '6379'))

    REDIS_OBJECTS_LIFETIME: int = 15 * 60

    def __post_init__(self) -> None:
        for _field in self.__slots__:
            if not getattr(self, _field):
                raise AttributeError(f'{_field} was not provided in .env file')

    @property
    def redis_url(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    def get_async_mongo_client(self) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(host=self.MONGO_HOST, port=self.MONGO_PORT)

    def mongodb_user_collection(self) -> AsyncIOMotorCollection:
        return self.get_async_mongo_client()['users_db']['users']


@dataclass(repr=False, slots=True, eq=False, frozen=True)
class RedisConfig:
    GROUP_SCHEMA: tuple = field(default=(
            TextField(name='$.id', as_name='id'),
            NumericField(name='$.group_size', as_name='group_size'),
            TextField(name='$.title', as_name='title'),
            TagField(name='$.game', as_name='game'),
            TagField(name='$.language', as_name='language'),
        ),
        kw_only=True,
    )
    GROUP_INDEX_PREFIX = 'group'

    @staticmethod
    async def get_async_redis_client() -> aioredis.Redis:
        config = get_conf()
        return await aioredis.from_url(config.redis_url)

    def create_indexes(self) -> bool:
        config = get_conf()
        r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
        rs = r.ft('idx:groups')
        rs.create_index(
            self.GROUP_SCHEMA,
            definition=IndexDefinition(
                prefix=[f'{self.GROUP_INDEX_PREFIX}:'], index_type=IndexType.JSON
            )
        )
        return True


@cache
def get_conf() -> Config:
    return Config()
