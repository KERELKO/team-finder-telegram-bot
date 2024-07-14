from mongorepo.asyncio.decorators import async_mongo_repository
from mongorepo import Access

import orjson

from redis.commands.search.query import Query
from redis.commands.search.result import Result

from src.common.config import RedisConfig, get_conf
from src.common.entities import Group, User
from src.common.filters import GroupFilters, Pagination

from .base import AbstractUserRepository, AbstractGroupRepository


@async_mongo_repository(method_access=Access.PROTECTED)
class MongoUserRepository(AbstractUserRepository):
    class Meta:
        dto = User
        collection = get_conf().mongodb_user_collection()

    async def get_by_id(self, id: int) -> User | None:
        return await self._get(id=id)  # type: ignore

    async def add(self, user: User) -> User:
        await self._add(dto=user)  # type: ignore
        return user


class RedisGroupRepository(AbstractGroupRepository):
    def __init__(self) -> None:
        self.config = RedisConfig()

    async def client(self):
        """Async redis client"""
        return await self.config.get_async_redis_client()

    async def add(self, group: Group) -> Group:
        r = await self.client()
        key = f'{self.config.GROUP_INDEX_PREFIX}{group.id}'
        async with r.pipeline(transaction=True) as pipe:
            await pipe.execute_command('JSON.SET', key, '.', orjson.dumps(group.asdict()))
            await pipe.expire(key, get_conf().REDIS_OBJECTS_LIFETIME)
            await pipe.execute()
        await r.aclose()
        return group

    async def search(self, filters: GroupFilters, pag: Pagination) -> list[Group]:
        search_parts = []

        if filters.size is not None:
            search_parts.append(f'@size:[{filters.size} {filters.size}]')

        if filters.language_code is not None:
            search_parts.append(f'@language:[{filters.language_code} {filters.language_code}]')

        if filters.game_code is not None:
            search_parts.append(f'@game:[{filters.game_code} {filters.game_code}]')

        search_string = ' '.join(search_parts) if search_parts else '*'

        r = await self.client()
        rs = r.ft(self.config.GROUP_INDEX_NAME)
        result: Result = await rs.search(
            Query(search_string).paging(pag.offset, pag.limit)
        )  # type: ignore
        groups = [Group(**orjson.loads(doc.__dict__['json'])) for doc in result.docs]

        await r.aclose()
        return groups
