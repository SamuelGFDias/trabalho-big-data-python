from extensions import Terminal
from interfaces import IPage


class BasePage(IPage):
    main_page: IPage | None = None

    def __init__(self):
        pass

    def show(self):
        Terminal.clear()
        BasePage.main_page.show() if BasePage.main_page else None
