from extensions import Terminal
from interfaces import Page


class BasePage(Page):
    main_page: Page | None = None

    def __init__(self):
        pass

    def show(self):
        Terminal.clear()
        BasePage.main_page.show() if BasePage.main_page else None
