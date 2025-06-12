import os
import platform

from extensions.string_extension import is_null_or_empty


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

            try:
                if '.' in value or ',' in value:
                    return float(value.replace(',', '.'))
                else:
                    return int(value)
            except ValueError:
                Terminal.read_key("Informe um número válido.")

    @staticmethod
    def read_string(message: str, default: str | None = None, clear: bool = True):
        while True:
            if clear:
                Terminal.clear()
            value = input(message)

            if not is_null_or_empty(value):
                return value
            elif default:
                return default

            Terminal.read_key("Informe um valor válido")
