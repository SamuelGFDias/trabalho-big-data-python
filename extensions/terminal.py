import os
import platform

from extensions.string_extension import isnullorempty


class Terminal:

    @staticmethod
    def clear():
        # Detecta o sistema operacional
        system = platform.system()

        # Comando para limpar o terminal baseado no sistema operacional
        if system == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    @staticmethod
    def read_key(message: str | None = None) -> str:
        key = input(message + '\n' if message else '' + "Pressione qualquer tecla para continuar. ")
        return key

    @staticmethod
    def read_number(message: str, clear: bool = True) -> int | float:
        while True:
            if clear:
                Terminal.clear()
            value = input(message)

            if value.isnumeric():
                if value.isdigit():
                    value = int(value)
                else:
                    value = float(value)
                return value

            Terminal.read_key("Informe um número válido.")

    @staticmethod
    def read_string(message: str, default: str | None = None, clear: bool = True):
        while True:
            if clear:
                Terminal.clear()
            value = input(message)

            if not isnullorempty(value):
                return value
            elif default:
                return default

            Terminal.read_key("Informe um valor válido válido.")
