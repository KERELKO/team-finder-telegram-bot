from mongorepo.implement import implement
from mongorepo.implement.methods import GetMethod, AddMethod
from mongorepo import set_meta_attrs

from team_bot.domain.entities.users import User

from team_bot.infra.repositories.base import AbstractUserRepository


@implement(
    GetMethod(AbstractUserRepository.get_by_id, filters=['id']),
    AddMethod(AbstractUserRepository.add, dto='user'),
)
@set_meta_attrs(dto_type=User)
class MongoUserRepository:
    ...
