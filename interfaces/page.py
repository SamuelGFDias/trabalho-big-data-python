from abc import ABC, abstractmethod


class IPage(ABC):

    @abstractmethod
    def show(self) -> None:
        pass
