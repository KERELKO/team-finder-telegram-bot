from abc import abstractmethod, ABC

from src.common.entities import Group
from src.common.filters import GroupFilters


class AbstractGroupManager(ABC):
    @abstractmethod
    async def add_group(self, group: Group) -> int:
        ...

    @abstractmethod
    async def get_group_by_filter(self, filters: GroupFilters) -> list[Group]:
        ...
