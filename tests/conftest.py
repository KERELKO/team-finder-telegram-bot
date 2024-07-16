import random

import pytest

from src.domain.entities import Group, Team, User
from src.domain.entities.games import AbstractGame, Game, games


@pytest.fixture
def game() -> Game:
    return Game(id=random.randint(1, 10), rating=random.randint(1, 10))


@pytest.fixture
def game_list() -> list[type[AbstractGame]]:
    return games()


@pytest.fixture
def user(game: Game) -> User:
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
        owner_id=owner_id,
        title=f'test_{owner_id}',
        description='test group',
    )


@pytest.fixture
def team(game: Game) -> Team:
    owner_id = random.randint(1, 12385)
    return Team(
        owner_id=owner_id,
        title=f'test_{owner_id}',
        size=random.randint(2, 10),
        game_id=game.id,
        game_rating=game.rating,
        description='test group',
    )