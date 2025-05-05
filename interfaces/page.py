from abc import ABC, abstractmethod


class Page(ABC):

    @abstractmethod
    def show(self) -> None:
        pass
