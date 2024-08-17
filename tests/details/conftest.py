import random

from src.domain.entities.users import Group, Team


def group_factory() -> Group:
    return Group(
        owner_id=random.randint(0, 20000),
        title=f'test_{random.randint(0, 20000)}',
    )


def team_factory() -> Team:
    return Team(
        players_to_fill=random.randint(2, 5),
        game_id=random.randint(1, 8),
        game_rating=random.randint(1, 10),
        owner_id=random.randint(1, 97098),
        title=f'Team #{random.randint(1, 96076)}',
    )
