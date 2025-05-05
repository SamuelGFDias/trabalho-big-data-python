from typing import Tuple, Callable, TypeAlias

from extensions import Terminal
from interfaces import Page

OpcaoMenu: TypeAlias = Tuple[str, Callable]


class MenuPage(Page):
    opcoes: dict[int, OpcaoMenu]

    def __init__(self, opcoes: dict[int, OpcaoMenu]):
        super().__init__()
        self.opcoes = opcoes

    def show(self) -> None:
        Terminal.clear()

        message = ""
        for op in self.opcoes:
            message += f"{op} - {self.opcoes[op][0]}\n"

        message += "\nSelecione uma das opções acima: "
        selected_option = Terminal.read_number(message)

        self.opcoes[selected_option][1]()
