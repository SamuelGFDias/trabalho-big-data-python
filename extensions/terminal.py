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