from .base import BaseGame, GameCollection


CS2 = BaseGame(
    id=1,
    name='Counter Strike 2',
    _ranks={
        1: 'Silver',
        2: 'Gold Nova',
        3: 'Master Guardian',
        4: 'Legendary Eagle',
        5: 'Global Elite',
    }
)

AOE2 = BaseGame(
    id=2,
    name='Age of empires 2',
    _ranks={
        1: '600',
        2: '800',
        3: '1000',
        4: '1200',
        5: '1400',
        6: '1600',
        7: '1800',
        8: '2000',
    },
)


class ImperativeGameCollection(GameCollection):
    def __init__(self, games: list[BaseGame] | None = None) -> None:
        self.games = games or [AOE2, CS2]
        self.i = 0

    def __next__(self) -> BaseGame:
        try:
            item = self.games[self.i]
            self.i += 1
            return item
        except IndexError:
            raise StopIteration
