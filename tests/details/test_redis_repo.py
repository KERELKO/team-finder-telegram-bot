import pytest

from src.domain.entities import Team
from src.domain.entities.games import AOE2
from src.common.filters import TeamFilters, Pagination
from src.infra.repositories.impl import RedisTeamRepository

from .conftest import team_factory


@pytest.mark.asyncio
async def test_can_add_teams():
    repo = RedisTeamRepository()

    team_1 = team_factory()
    team_2 = team_factory()
    team_3 = team_factory()

    await repo.add(team_1)
    await repo.add(team_2)
    await repo.add(team_3)

    assert True


@pytest.mark.asyncio
async def test_can_find_team_with_search():
    team = team_factory()
    team.game_id = AOE2.id
    team.game_rating = 6

    repo = RedisTeamRepository()

    await repo.add(team)

    searched_teams = await repo.search(
        filters=TeamFilters(game_id=team.game_id),
        pag=Pagination(),
    )
    assert len(searched_teams) > 0

    first_team = searched_teams[0]

    assert first_team.game_id == AOE2.id


@pytest.mark.asyncio
async def test_multiple_search_filters():
    team = Team(
        owner_id=1,
        title='for search',
        size=4,
        game_id=AOE2.id,
        game_rating=5,
    )

    repo = RedisTeamRepository()
    await repo.add(team)

    searched_teams = await repo.search(
        TeamFilters(
            game_id=team.game_id,
            size=team.size,
            min_rating=3,
            max_rating=5,
        ),
        Pagination(limit=10),
    )

    assert len(searched_teams) > 0

    searched_team = searched_teams[0]

    assert searched_team.game_id == team.game_id
    assert searched_team.size == team.size
    assert 3 <= searched_team.game_rating <= 8
