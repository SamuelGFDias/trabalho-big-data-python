from time import sleep
from typing import Callable

from pages import MenuPage, BasePage
from pages.decision_tree_page import DecisionTreePage
from pages.register_page import RegisterPage


def sair(message: str) -> Callable[[], None]:
    def exit_system():
        print(message, end='', flush=True)
        for _ in range(3):
            sleep(0.5)
            print('.', end='', flush=True)
        print()
        exit()

    return exit_system


def main():
    opcoes_do_menu = {
        1: ('Base Register', RegisterPage(r'assets/config.json').show),
        2: ('Exibir Árvore de Decisão', DecisionTreePage().show),
        3: ('Exibir SVM c/ Pipeline', None),
        4: ('Exibir SVM s/ Pipeline', None),
        5: ('Sair', sair("Bye Bye")),
    }

    menu = MenuPage(opcoes_do_menu)
    BasePage.main_page = menu
    screen = BasePage()
    screen.show()


if __name__ == '__main__':
    main()
