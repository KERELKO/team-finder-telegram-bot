import random
import uuid

import pytest

from team_bot.domain.entities.users import Group, Team
from team_bot.infra.di import Container


@pytest.fixture
def container() -> Container:
    container = Container()
    return container


def id_factory():
    return str(lambda: uuid.uuid4())


def group_factory() -> Group:
    return Group(
        id=id_factory(),
        owner_id=random.randint(0, 20000),
        title=f'test_{random.randint(0, 20000)}',
    )


def team_factory() -> Team:
    return Team(
        id=id_factory(),
        players_to_fill=random.randint(2, 5),
        game_id=random.randint(1, 8),
        game_rating=random.randint(1, 10),
        owner_id=random.randint(1, 97098),
        title=f'Team #{random.randint(1, 96076)}',
    )
