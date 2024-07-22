import pytest
from src.domain.entities import User
from src.domain.entities.games import Game
from src.infra.repositories.impl import MongoUserRepository


@pytest.mark.asyncio
async def test_add_and_get_operations_with_mongo_repo() -> None:
    repo = MongoUserRepository()
    user = User(
        id=1,
        username='admin',
        games=[Game(id=1, rating=4), Game(id=2, rating=6)],
    )
    user_id = user.id

    await repo.add(user)

    resolved_user: User | None = await repo.get_by_id(id=user_id)  # type: ignore
    assert resolved_user is not None
    assert resolved_user.username == 'admin'

    assert len(resolved_user.games) == 2
    game = resolved_user.games[0]
    assert game.id == 1
