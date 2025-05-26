from team_bot.domain.entities.games.base import BaseGame, GameCollection


def get_game_by_id(game_id: int, collection: GameCollection) -> BaseGame | None:
    for game in collection:
        if game.id == game_id:
            return game
    return None


def get_game_by_name(game_name: str, collection: GameCollection) -> BaseGame | None:
    for game in collection:
        if game.name == game_name:
            return game
    return None


def get_game_rank_value(game: BaseGame, key: int, default: str | None = None) -> str | None:
    for _key, value in game.ranks().items():  # type: ignore
        if _key == key:
            return value
    return default
