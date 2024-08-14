from src.common.di import Container
from src.domain.entities.games.base import AbstractGame, AbstractGames


def get_game_by_id(game_id: int) -> AbstractGame | None:
    games: AbstractGames = Container.resolve(AbstractGames)
    for game in games:
        if game.id == game_id:
            return game
    return None


def get_game_by_name(game_name: str) -> AbstractGame | None:
    games: AbstractGames = Container.resolve(AbstractGames)
    for game in games:
        if game.name == game_name:
            return game
    return None


def get_game_rank_value(
    game: AbstractGame, key: int, default: str | None = None
) -> str | None:
    for _key, value in game.ranks().items():  # type: ignore
        if _key == key:
            return value
    return default
