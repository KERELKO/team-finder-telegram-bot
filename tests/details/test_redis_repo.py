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
        players_to_fill=4,
        game_id=AOE2.id,
        game_rating=5,
    )

    repo = RedisTeamRepository()
    await repo.add(team)

    searched_teams = await repo.search(
        TeamFilters(
            game_id=team.game_id,
            min_rating=3,
            max_rating=5,
        ),
        Pagination(limit=10),
    )

    assert len(searched_teams) > 0

    searched_team = searched_teams[0]

    assert searched_team.game_id == team.game_id
    assert searched_team.players_to_fill == team.players_to_fill
    assert 3 <= searched_team.game_rating <= 5


@pytest.mark.asyncio
async def test_can_find_team_by_owner_id():
    team = Team(
        owner_id=780,
        title='for search',
        players_to_fill=4,
        game_id=AOE2.id,
        game_rating=5,
    )

    repo = RedisTeamRepository()
    await repo.add(team)

    team = await repo.get_by_owner_id(owner_id=team.owner_id)
    assert team is not None

    assert team.players_to_fill == 4
    assert team.game_id == AOE2.id


@pytest.mark.asyncio
async def test_can_delete_team_by_owner_id():
    team = Team(
        owner_id=78999,
        title='for search',
        players_to_fill=4,
        game_id=AOE2.id,
        game_rating=5,
    )

    repo = RedisTeamRepository()
    await repo.add(team)

    is_deleted = await repo.delete_by_owner_id(owner_id=team.owner_id)

    assert is_deleted


@pytest.mark.asyncio
async def test_can_change_players_to_fill_field():
    team = Team(
        owner_id=808080,
        title='for search',
        players_to_fill=4,
        game_id=AOE2.id,
        game_rating=5,
    )

    repo = RedisTeamRepository()
    await repo.add(team)

    await repo.update_players_to_fill(team.id, 3)

    updated_team = await repo.get_by_owner_id(team.owner_id)

    assert updated_team is not None
    assert updated_team.players_to_fill + 1 == team.players_to_fill
