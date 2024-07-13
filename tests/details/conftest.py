import random

from src.common.constants import Game, Language
from src.common.entities import Group


def group_factory() -> Group:
    return Group(
        owner_id=random.randint(0, 20000),
        title=f'test_{random.randint(0, 20000)}',
        game=random.choice([x for x in Game]),
        language=random.choice([x for x in Language]),
        size=random.randint(2, 5),
    )