import random
import uuid

import pytest

from team_bot.domain.entities.users import Group, Team, User, GameData
from team_bot.domain.entities.games.base import BaseGame
from team_bot.domain.entities.games.impl import ImperativeGameCollection


def id_factory():
    return str(lambda: uuid.uuid4())


@pytest.fixture
def game() -> GameData:
    return GameData(id=random.randint(1, 10), rating=random.randint(1, 10))


@pytest.fixture
def game_list() -> list[BaseGame]:
    return ImperativeGameCollection().factory()


@pytest.fixture
def user(game: GameData) -> User:
    user_id = random.randint(1, 12385)
    return User(
        id=user_id,
        username=f'user_{user_id}',
        games=list[game],  # type: ignore
    )


@pytest.fixture
def group() -> Group:
    owner_id = random.randint(1, 12385)
    return Group(
        id=id_factory(),
        owner_id=owner_id,
        title=f'test_{owner_id}',
        description='test group',
    )


@pytest.fixture
def team(game: GameData) -> Team:
    owner_id = random.randint(1, 12385)
    return Team(
        id=id_factory(),
        owner_id=owner_id,
        title=f'test_{owner_id}',
        players_to_fill=random.randint(2, 10),
        game_id=game.id,
        game_rating=game.rating,
        description='test group',
    )
