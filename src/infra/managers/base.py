from abc import abstractmethod, ABC


class AbstractGroupManager(ABC):
    @abstractmethod
    async def add_group(self, title: str, link: str) -> int:
        ...

    @abstractmethod
    async def get_group_by_filter(self):
        ...
