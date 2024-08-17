from dataclasses import asdict

from mongorepo.asyncio.classes import AsyncBasedMongoRepository

import orjson

from redis.asyncio import Redis
from redis.commands.search.query import Query
from redis.commands.search.result import Result

from src.common.config import RedisConfig, get_conf
from src.domain.entities.users import Team, User
from src.common.filters import TeamFilters, Pagination

from .base import AbstractUserRepository, AbstractTeamRepository


class MongoUserRepository(AsyncBasedMongoRepository[User], AbstractUserRepository):
    class Meta:
        collection = get_conf().mongodb_user_collection()

    async def get_by_id(self, id: int) -> User | None:
        return await super().get(id=id)

    async def add(self, user: User) -> User:
        await super().add(dto=user)
        return user


class RedisTeamRepository(AbstractTeamRepository):
    def __init__(self) -> None:
        self.config = RedisConfig()
        self._client: Redis | None = None

    async def get_client(self) -> Redis:
        """Async redis client"""
        if self._client is None:
            self._client = await self.config.get_async_redis_client()
        return self._client

    async def close_connection(self) -> None:
        if self._client is not None:
            await self._client.aclose()
        self._client = None

    async def add(self, team: Team) -> Team:
        r = await self.get_client()
        key = f'{self.config.TEAM_INDEX_PREFIX}{team.id}'
        async with r.pipeline(transaction=True) as pipe:
            await pipe.execute_command('JSON.SET', key, '.', orjson.dumps(asdict(team)))
            await pipe.expire(key, get_conf().REDIS_OBJECTS_LIFETIME)
            await pipe.execute()
        await self.close_connection()
        return team

    async def get_by_owner_id(self, owner_id: int, _close_connection: bool = True) -> Team | None:
        r = await self.get_client()
        query_string = f'@owner_id:[{owner_id} {owner_id}]'
        rs = r.ft(self.config.TEAM_INDEX_NAME)
        result: Result = await rs.search(Query(query_string))  # type: ignore
        if _close_connection:
            await self.close_connection()
        if not result.docs:
            return None
        return Team(**orjson.loads(result.docs[0].__dict__['json']))

    async def delete_by_owner_id(self, owner_id: int) -> bool:
        team = await self.get_by_owner_id(owner_id=owner_id, _close_connection=False)
        if not team:
            return False
        key = f'{self.config.TEAM_INDEX_PREFIX}{team.id}'
        r = await self.get_client()
        async with r.pipeline() as pipe:  # type: ignore
            await pipe.execute_command('JSON.DEL', key)
            await pipe.execute()
        await self.close_connection()
        return True

    async def update_players_count(self, team_id: str, count: int) -> None:
        r = await self.get_client()
        key = f'{self.config.TEAM_INDEX_PREFIX}{team_id}'
        async with r.pipeline() as pipe:  # type: ignore
            await pipe.execute_command('JSON.SET', key, '$.players_to_fill', f'{count}')
            await pipe.execute()
        await self.close_connection()

    async def search(self, filters: TeamFilters, pag: Pagination) -> list[Team]:
        search_parts = []

        if filters.game_id is not None:
            search_parts.append(f'@game_id:[{filters.game_id} {filters.game_id}]')

        if filters.max_rating or filters.min_rating:
            mi = filters.min_rating
            ma = filters.max_rating
            search_parts.append(f'@game_rating:[{mi if mi else 1} {ma if ma else 1000}]')

        search_string = ' '.join(search_parts) if search_parts else '*'

        r = await self.get_client()
        rs = r.ft(self.config.TEAM_INDEX_NAME)
        result: Result = await rs.search(
            Query(search_string).paging(pag.offset, pag.limit)
        )  # type: ignore
        await self.close_connection()
        teams = [Team(**orjson.loads(doc.__dict__['json'])) for doc in result.docs]
        return teams
