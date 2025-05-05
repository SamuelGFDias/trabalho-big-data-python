from typing import TypeAlias, Tuple, Callable, Dict

from extensions import Terminal
from interfaces import IPage

OpcaoMenu: TypeAlias = Tuple[str, Callable]


class ListablePage(IPage):
    def __init__(self):
        self.opcoes: Dict[int, OpcaoMenu] = {}

    def show(self) -> None:
        while True:
            Terminal.clear()

            message = ""
            for op in self.opcoes:
                message += f"{op} - {self.opcoes[op][0]}\n"

            message += "\nSelecione uma das opções acima: "
            selected_option = Terminal.read_number(message)

            if selected_option not in self.opcoes:
                print("Opção inválida.")
                Terminal.read_key()
                continue

            self.opcoes[selected_option][1]()

            # Se a opção for "Sair", encerramos o loop
            if self.opcoes[selected_option][0].lower() == "sair":
                break