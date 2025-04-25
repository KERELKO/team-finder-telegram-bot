from mongorepo.implement import implement
from mongorepo.implement.methods import GetMethod, AddMethod

from src.domain.entities.users import User

from src.infra.repositories.base import AbstractUserRepository


@implement(
    GetMethod(AbstractUserRepository.get_by_id, filters=['id']),
    AddMethod(AbstractUserRepository.add, dto='user'),
)
class MongoUserRepository:
    class Meta:
        dto = User
