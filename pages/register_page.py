import csv
from pathlib import Path

from domain import BaseCsv
from extensions import JsonExtension, Terminal, isnullorempty, read_csv_columns
from interfaces import Page
from pages import BasePage


class RegisterPage(BasePage, Page):
    bases: list[BaseCsv]

    def __init__(self, path: str | None = None):
        super().__init__()
        self.bases = JsonExtension.load(path) if path else []
        self.opcoes = {
            1: ('Listar Bases', self.list_bases),
            2: ('Registrar Base', self.register_base),
            3: ('Atualizar Base', self.update_base),
            4: ('Remover Base', self.remove_base),
            5: ('Sair', super().show)
        }
        pass

    def show(self):
        Terminal.clear()

        message = ""
        for op in self.opcoes:
            message += f"{op} - {self.opcoes[op][0]}\n"

        message += "\nSelecione uma das opções acima: "

        selected_option = Terminal.read_number(message)
        self.opcoes[selected_option][1]()
        self.show()

    def list_bases(self):
        Terminal.clear()

        message = ""
        for i, base in enumerate(self.bases):
            message += f"{i} - {base.name}\n"

        print(message if not isnullorempty(message) else f"Nenhuma base registrada;\n")
        Terminal.read_key()

    def register_base(self):
        Terminal.clear()
        print("=== Registro de Nova Base ===\n")

        name = Terminal.read_string("Nome da base: ")
        path = Terminal.read_string("Caminho do arquivo CSV: ")
        encoding = Terminal.read_string("Encoding [utf-8]: ", default="utf-8")
        delimiter = Terminal.read_string("Delimitador [,]: ", default=",")

        if not Path(path).exists():
            print("Arquivo não encontrado.")
            Terminal.read_key()
            return

        # Lê o cabeçalho do CSV
        try:
            columns = read_csv_columns(path, encoding, delimiter)
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            Terminal.read_key()
            return

        print("\nColunas encontradas:")
        for i, col in enumerate(columns):
            print(f"{i} - {col}")

        # Entradas e saídas
        input_indexes = Terminal.read_string("\nÍndices das colunas de entrada (separados por vírgula): ")
        exit_indexes = Terminal.read_string("Índices das colunas de saída (separados por vírgula): ")

        def get_selected(indices: str):
            try:
                return [columns[int(ind.strip())] for ind in indices.split(',') if ind.strip().isdigit()]
            except Exception:
                return []

        input_columns = get_selected(input_indexes)
        exit_columns = get_selected(exit_indexes)

        base = BaseCsv()
        base.name = name
        base.path = path
        base.encoding = encoding
        base.delimiter = delimiter
        base.all_columns = columns
        base.input_columns = input_columns
        base.exit_columns = exit_columns

        self.bases.append(base)
        JsonExtension.save("assets/config.json", self.bases)

        print("\nBase registrada com sucesso!")
        Terminal.read_key()

    def update_base(self):
        Terminal.clear()
        print("=== Atualizar Base ===\n")

        if not self.bases:
            print("Nenhuma base registrada.")
            Terminal.read_key()
            return

        for i, base in enumerate(self.bases):
            print(f"{i} - {base.name}")

        idx = Terminal.read_number("\nSelecione o índice da base a atualizar: ")

        if not (0 <= idx < len(self.bases)):
            print("Índice inválido.")
            Terminal.read_key()
            return

        base = self.bases[idx]

        # Atualiza informações básicas
        base.name = Terminal.read_string(f"Nome [{base.name}]: ", default=base.name)
        base.path = Terminal.read_string(f"Caminho [{base.path}]: ", default=base.path)
        base.encoding = Terminal.read_string(f"Encoding [{base.encoding or 'utf-8'}]: ",
                                             default=base.encoding or "utf-8")
        base.delimiter = Terminal.read_string(f"Delimitador [{base.delimiter or ','}]: ", default=base.delimiter or ",")

        # Relê colunas, se o caminho for válido
        try:
            columns = read_csv_columns(base.path, base.encoding, base.delimiter)
            base.all_columns = columns
        except Exception as e:
            print(f"Erro ao reler as colunas do CSV: {e}")
            Terminal.read_key()
            return

        print("\nColunas encontradas:")
        for i, col in enumerate(base.all_columns):
            print(f"{i} - {col}")

        print(f"\nColunas de entrada atuais: {', '.join(base.input_columns or [])}")
        input_indexes = Terminal.read_string("Índices das colunas de entrada (Enter para manter): ",
                                             default=base.input_columns)

        print(f"Colunas de saída atuais: {', '.join(base.exit_columns or [])}")
        exit_indexes = Terminal.read_string("Índices das colunas de saída (Enter para manter): ",
                                            default=base.input_columns)

        def get_selected(indices: str, original: list[str]):
            try:
                return [base.all_columns[int(i.strip())] for i in indices.split(',') if i.strip().isdigit()]
            except Exception:
                return original

        base.input_columns = get_selected(input_indexes, base.input_columns)
        base.exit_columns = get_selected(exit_indexes, base.exit_columns)

        JsonExtension.save("assets/config.json", self.bases)

        print("\nBase atualizada com sucesso!")
        Terminal.read_key()

    def remove_base(self):
        Terminal.clear()
        print("=== Remover Base ===\n")

        if not self.bases:
            print("Nenhuma base registrada.")
            Terminal.read_key()
            return

        for i, base in enumerate(self.bases):
            print(f"{i} - {base.name}")

        idx = Terminal.read_number("\nSelecione o índice da base a remover: ")

        if not (0 <= idx < len(self.bases)):
            print("Índice inválido.")
            Terminal.read_key()
            return

        nome = self.bases[idx].name
        confirm = Terminal.read_string(f"Tem certeza que deseja remover '{nome}'? (s/n): ")

        if confirm.lower() == 's':
            self.bases.pop(idx)
            JsonExtension.save("assets/config.json", self.bases)
            print("Base removida com sucesso!")
        else:
            print("Operação cancelada.")

        Terminal.read_key()
