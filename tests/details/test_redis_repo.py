import pytest

from src.common.constants import Game
from src.common.entities import Group
from src.common.filters import GroupFilters, Pagination
from src.infra.repositories.impl import RedisGroupRepository

from .conftest import group_factory


@pytest.mark.asyncio
async def test_can_add_groups():
    repo = RedisGroupRepository()

    group_1 = group_factory()
    group_2 = group_factory()
    group_3 = group_factory()

    await repo.add(group_1)
    await repo.add(group_2)
    await repo.add(group_3)

    assert True


@pytest.mark.asyncio
async def test_can_find_group_with_search():
    group = group_factory()
    group.game = Game.AOE2

    repo = RedisGroupRepository()

    await repo.add(group)

    searched_groups = await repo.search(
        filters=GroupFilters(game_code=group.game.value),
        pag=Pagination(),
    )
    assert len(searched_groups) > 0

    first_group = searched_groups[0]

    assert first_group.game == Game.AOE2


@pytest.mark.asyncio
async def test_multiple_search_filters():
    group = Group(
        owner_id=1,
        title='for search',
        size=4,
        game=Game.AOE2,
    )

    repo = RedisGroupRepository()
    await repo.add(group)

    searched_group, *_ = await repo.search(
        GroupFilters(
            game_code=group.game.value, size=group.size
        ),
        Pagination(limit=10),
    )

    assert searched_group.game == group.game
    assert searched_group.size == group.size
