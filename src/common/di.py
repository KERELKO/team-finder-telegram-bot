import logging
from functools import cache

import punq
from mongorepo import use_collection

from src.common.config import get_conf
from src.domain.entities.games.base import Games
from src.domain.entities.games.impl import GamesFromFile
from src.infra.repositories.base import AbstractTeamRepository, AbstractUserRepository

from src.infra.repositories.team.redis import RedisTeamRepository
from src.infra.repositories.user.mongo import MongoUserRepository


class Container:
    @staticmethod
    def get() -> punq.Container:
        return Container._init()

    @staticmethod
    def resolve[T](base_cls: type[T]) -> T:
        return Container.get().resolve(base_cls)  # type: ignore

    @staticmethod
    @cache
    def _init() -> punq.Container:
        container = punq.Container()

        config = get_conf()

        logger = logging.getLogger('Logger')
        container.register(logging.Logger, instance=logger)

        container.register(
            AbstractUserRepository,
            instance=use_collection(config.mongodb_user_collection())(MongoUserRepository()),
        )
        container.register(AbstractTeamRepository, RedisTeamRepository)

        container.register(Games, factory=GamesFromFile.factory)

        return container
