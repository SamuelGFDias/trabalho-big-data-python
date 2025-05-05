from typing import Tuple, Callable, TypeAlias
from pages.listable_page import ListablePage

OpcaoMenu: TypeAlias = Tuple[str, Callable]


class MenuPage(ListablePage):
    def __init__(self, opcoes: dict[int, OpcaoMenu]):
        super().__init__()
        self.opcoes = opcoes
