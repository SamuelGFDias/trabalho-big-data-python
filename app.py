import sys
from time import sleep
from typing import Callable

from pages import MenuPage, BasePage
from pages import DecisionTreePage, RegisterPage, SvmSemPipelinePage, SvmComPipelinePage


def sair(message: str) -> Callable[[], None]:
    def exit_system():
        print(message, end='', flush=True)
        for _ in range(3):
            sleep(0.5)
            print('.', end='', flush=True)
        print()
        sys.exit()()

    return exit_system


def main():
    path = r'config.json'
    opcoes_do_menu = {
        1: ('Base Register', RegisterPage(path).show),
        2: ('Exibir Árvore de Decisão', DecisionTreePage(path).show),
        3: ('Exibir SVM c/ Pipeline', SvmComPipelinePage(path).show),
        4: ('Exibir SVM s/ Pipeline', SvmSemPipelinePage(path).show),
        5: ('Sair', sair("Bye Bye")),
    }

    menu = MenuPage(opcoes_do_menu)
    BasePage.main_page = menu
    screen = BasePage()
    screen.show()


if __name__ == '__main__':
    main()
# pyinstaller --onefile --name BigDataApp app.py