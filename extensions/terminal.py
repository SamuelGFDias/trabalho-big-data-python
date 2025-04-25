import os
import platform

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
    def read_key(message:str | None = None) -> str:
        key = input(message + '\n' if message else '' + "Pressione qualquer tecla para continuar. ")
        return key
    
    @staticmethod
    def read_number(message:str):
        while True:
            Terminal.clear()
            
            value = input(message)

            if value.isnumeric():
                return value
            
            Terminal.read_key()
    