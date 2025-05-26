from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import AsyncGenerator

import orjson

from redis.asyncio import Redis
from redis.commands.search.query import Query
from redis.commands.search.result import Result

from team_bot.common.config import RedisConfig
from team_bot.domain.entities.users import Team

from team_bot.infra.repositories.base import AbstractTeamRepository, TeamFilters, Pagination


class RedisTeamRepository(AbstractTeamRepository):
    def __init__(self, config: RedisConfig) -> None:
        self._config = config
        self._client: Redis | None = None

    @asynccontextmanager
    async def client(self) -> AsyncGenerator[Redis, None]:
        try:
            yield await self._get_client()
        finally:
            await self._close_connection()

    async def _get_client(self) -> Redis:
        """Async redis client"""
        if self._client is None:
            self._client = await self._config.get_async_redis_client()
        return self._client

    async def _close_connection(self) -> None:
        if self._client is not None:
            await self._client.aclose()
        self._client = None

    async def add(self, team: Team) -> Team:
        async with self.client() as r:
            key = f'{self._config.TEAM_INDEX_PREFIX}{team.id}'
            async with r.pipeline(transaction=True) as pipe:
                await pipe.execute_command('JSON.SET', key, '.', orjson.dumps(asdict(team)))
                await pipe.expire(key, self._config.REDIS_OBJECTS_LIFETIME)
                await pipe.execute()
        return team

    async def get_by_owner_id(self, owner_id: int, _close_connection: bool = True) -> Team | None:
        r = await self._get_client()
        query_string = f'@owner_id:[{owner_id} {owner_id}]'
        rs = r.ft(self._config.TEAM_INDEX_NAME)
        result: Result = await rs.search(Query(query_string))  # type: ignore
        if _close_connection:
            await self._close_connection()
        if not result.docs:
            return None
        return Team(**orjson.loads(result.docs[0].__dict__['json']))

    async def delete_by_owner_id(self, owner_id: int) -> bool:
        team = await self.get_by_owner_id(owner_id=owner_id, _close_connection=False)
        if not team:
            return False
        key = f'{self._config.TEAM_INDEX_PREFIX}{team.id}'
        async with self.client() as r:
            async with r.pipeline() as pipe:  # type: ignore
                await pipe.execute_command('JSON.DEL', key)
                await pipe.execute()
        return True

    async def update_players_count(self, team_id: str, count: int) -> None:
        async with self.client() as r:
            key = f'{self._config.TEAM_INDEX_PREFIX}{team_id}'
            async with r.pipeline() as pipe:  # type: ignore
                await pipe.execute_command('JSON.SET', key, '$.players_to_fill', f'{count}')
                await pipe.execute()

    async def search(self, filters: TeamFilters, pag: Pagination) -> list[Team]:
        search_parts = []

        if filters.game_id is not None:
            search_parts.append(f'@game_id:[{filters.game_id} {filters.game_id}]')

        if filters.max_rating or filters.min_rating:
            mi = filters.min_rating
            ma = filters.max_rating
            search_parts.append(f'@game_rating:[{mi if mi else 1} {ma if ma else 1000}]')

        search_string = ' '.join(search_parts) if search_parts else '*'

        async with self.client() as r:
            rs = r.ft(self._config.TEAM_INDEX_NAME)
            result: Result = await rs.search(
                Query(search_string).paging(pag.offset, pag.limit)
            )  # type: ignore
        teams = [Team(**orjson.loads(doc.__dict__['json'])) for doc in result.docs]
        return teams
