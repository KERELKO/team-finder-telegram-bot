import json

from mongorepo.asyncio.decorators import async_mongo_repository
from mongorepo import Access

from src.common.config import RedisConfig, get_conf
from src.common.entities import Group, User
from src.common.filters import GroupFilters

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

    async def pool(self):
        return await self.config.get_async_redis_client()

    async def add(self, group: Group) -> Group:
        r = await self.pool()
        key = f'{self.config.GROUP_INDEX_PREFIX}:{group.id}'
        await r.execute_command('JSON.SET', key, '.', json.dumps(group.asdict()), 'NX')
        await r.expire(key, get_conf().REDIS_OBJECTS_LIFETIME)
        await r.close()
        return group

    async def get_by_filters(self, filters: GroupFilters) -> list[Group]:
        ...
