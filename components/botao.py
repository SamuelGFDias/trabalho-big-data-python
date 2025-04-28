from extensions import Event
import random

class Botao:
    def __init__(self):
        self.Click = Event()

    def clicar(self, *args, **kargs):
        self.Click.fire(*args, **kargs)