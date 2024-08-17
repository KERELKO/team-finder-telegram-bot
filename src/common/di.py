import logging
from functools import cache
from typing import Any, TypeVar

import punq

from src.domain.entities.games.base import AbstractGames
from src.domain.entities.games.impl import GamesFromFile
from src.infra.repositories.base import AbstractTeamRepository, AbstractUserRepository
from src.infra.repositories.impl import MongoUserRepository, RedisTeamRepository


BaseClass = TypeVar('BaseClass')
Implementation = TypeVar('Implementation')


class Container:
    @staticmethod
    def get() -> punq.Container:
        return Container._init()

    @staticmethod
    def resolve(base_cls: type[BaseClass]) -> Implementation | Any:  # type: ignore
        return Container.get().resolve(base_cls)

    @staticmethod
    @cache
    def _init() -> punq.Container:
        container = punq.Container()

        logger = logging.getLogger('Logger')
        container.register(logging.Logger, instance=logger)

        container.register(AbstractUserRepository, instance=MongoUserRepository())
        container.register(AbstractTeamRepository, RedisTeamRepository)

        container.register(AbstractGames, factory=GamesFromFile.factory)

        return container
