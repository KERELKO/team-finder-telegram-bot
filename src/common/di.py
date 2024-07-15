from functools import cache
from typing import Any, Type, TypeVar
import logging

import punq

from src.infra.repositories.base import AbstractTeamRepository, AbstractUserRepository
from src.infra.repositories.impl import MongoUserRepository, RedisTeamRepository


ABC = TypeVar('ABC')


class Container:
    @staticmethod
    def get() -> punq.Container:
        return Container._init()

    @staticmethod
    def resolve(base_cls: Type[ABC]) -> Any:
        return Container.get().resolve(base_cls)

    @cache
    @staticmethod
    def _init() -> punq.Container:
        container = punq.Container()

        logger = logging.getLogger('Logger')
        container.register(logging.Logger, instance=logger)

        container.register(AbstractUserRepository, MongoUserRepository)
        container.register(AbstractTeamRepository, RedisTeamRepository)

        return container
