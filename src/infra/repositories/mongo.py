from mongorepo.asyncio.decorators import async_mongo_repository
from mongorepo import Access

from src.common.entities import User
from src.common.config import get_conf

from .base import AbstractUserRepository


@async_mongo_repository(method_access=Access.PROTECTED)
class MongoUserRepository(AbstractUserRepository):
    class Meta:
        dto = User
        collection = get_conf().mongodb_user_collection()

    async def get_by_id(self, id: int) -> User:
        return await self._get(id=id)  # type: ignore

    async def add(self, user: User) -> User:
        await self._add(dto=user)  # type: ignore
        return user
