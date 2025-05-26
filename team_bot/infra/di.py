import logging
from functools import cache
from typing import cast

import punq  # type: ignore[import-untyped]
from mongorepo import use_collection

from team_bot.common.config import Config, RedisConfig
from team_bot.domain.entities.games.base import GameCollection
from team_bot.infra.game_collection.file import FileGameCollection
from team_bot.infra.repositories.base import AbstractTeamRepository, AbstractUserRepository

from team_bot.infra.repositories.team.redis import RedisTeamRepository
from team_bot.infra.repositories.user.mongo import MongoUserRepository


class Container:
    def __init__(self, punq_container: punq.Container | None = None) -> None:
        self.container = punq_container or self._init()

    def resolve[T](self, obj_type: type[T] | str, *args) -> T:
        return cast(T, self.container.resolve(obj_type))

    @staticmethod
    @cache
    def _init() -> punq.Container:
        container = punq.Container()

        config = Config()
        redis_config = RedisConfig()

        container.register(Config, instance=config, scope=punq.Scope.singleton)
        container.register(RedisConfig, instance=redis_config, scope=punq.Scope.singleton)

        logger = logging.getLogger('Logger')
        container.register(logging.Logger, instance=logger)

        container.register(
            AbstractUserRepository,
            instance=use_collection(config.mongodb_user_collection())(MongoUserRepository()),
        )
        container.register(AbstractTeamRepository, RedisTeamRepository)

        container.register(GameCollection, instance=FileGameCollection(config.games_json_path))

        return container
