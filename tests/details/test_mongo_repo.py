from typing import cast
import pytest

from team_bot.domain.entities.users import User, GameData
from team_bot.infra.repositories.user.mongo import MongoUserRepository, AbstractUserRepository


@pytest.mark.asyncio
async def test_add_and_get_operations_with_mongo_repo() -> None:
    repo = cast(AbstractUserRepository, MongoUserRepository())
    user = User(
        id=1,
        username='admin',
        games=[GameData(id=1, rating=4), GameData(id=2, rating=6)],
    )
    user_id = user.id

    await repo.add(user)

    resolved_user: User | None = await repo.get_by_id(id=user_id)  # type: ignore
    assert resolved_user is not None
    assert resolved_user.username == 'admin'

    assert len(resolved_user.games) == 2
    game = resolved_user.games[0]
    assert game.id == 1
