from dataclasses import asdict

from mongorepo.asyncio.decorators import async_mongo_repository
from mongorepo import Access

import orjson

from redis.commands.search.query import Query
from redis.commands.search.result import Result

from src.common.config import RedisConfig, get_conf
from src.domain.entities import Team, User
from src.common.filters import TeamFilters, Pagination

from .base import AbstractUserRepository, AbstractTeamRepository


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


class RedisTeamRepository(AbstractTeamRepository):
    def __init__(self) -> None:
        self.config = RedisConfig()

    async def client(self):
        """Async redis client"""
        return await self.config.get_async_redis_client()

    async def add(self, team: Team) -> Team:
        r = await self.client()
        key = f'{self.config.TEAM_INDEX_PREFIX}{team.id}'
        async with r.pipeline(transaction=True) as pipe:
            await pipe.execute_command('JSON.SET', key, '.', orjson.dumps(asdict(team)))
            await pipe.expire(key, get_conf().REDIS_OBJECTS_LIFETIME)
            await pipe.execute()
        await r.aclose()
        return team

    async def search(self, filters: TeamFilters, pag: Pagination) -> list[Team]:
        search_parts = []

        if filters.size is not None:
            search_parts.append(f'@size:[{filters.size} {filters.size}]')

        if filters.game_id is not None:
            search_parts.append(f'@game_id:[{filters.game_id} {filters.game_id}]')

        if filters.max_rating or filters.min_rating:
            mi = filters.min_rating
            ma = filters.max_rating
            search_parts.append(f'@game_rating:[{mi if mi else 0} {ma if ma else 1000}]')

        search_string = ' '.join(search_parts) if search_parts else '*'

        r = await self.client()
        rs = r.ft(self.config.TEAM_INDEX_NAME)
        result: Result = await rs.search(
            Query(search_string).paging(pag.offset, pag.limit)
        )  # type: ignore
        teams = [Team(**orjson.loads(doc.__dict__['json'])) for doc in result.docs]
        await r.aclose()
        return teams
