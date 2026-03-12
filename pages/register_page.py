from domain import BaseCsv
from extensions import JsonExtension, Terminal, isnullorempty, read_csv_columns
from extensions.csv_extension import show_columns, get_selected_indices, get_selected_indices_safe, \
    tentar_capturar_categorizador
from pages import BasePage, ListablePage
from pathlib import Path
import pandas as pd


class RegisterPage(ListablePage, BasePage):
    def __init__(self, path: str):
        super().__init__()
        self.path = path
        if not Path(path).exists():
            with open(path, 'w', encoding='utf-8') as f:
                f.write("[]")
        self.bases: list[BaseCsv] = JsonExtension.load(path)
        self.opcoes = {
            1: ('Listar Bases', self.list_bases),
            2: ('Registrar Base', self.register_base),
            3: ('Atualizar Base', self.update_base),
            4: ('Remover Base', self.remove_base),
            5: ('Sair', lambda: None)
        }

    def list_bases(self):
        Terminal.clear()

        if not self.bases:
            print("Nenhuma base registrada.\n")
        else:
            for i, base in enumerate(self.bases):
                print(f"{i} - {base.name}")
                print(f"  Caminho: {base.path}")
                print(f"  Encoding: {base.encoding}")
                print(f"  Delimitador: {base.delimiter}")
                print(f"  Colunas: {', '.join(base.all_columns)}")
                print(f"  Entrada: {', '.join(base.input_columns)}")
                print(f"  Saída: {', '.join(base.exit_columns)}")
                if base.categorize_fn_code:
                    print(f"  Categorizar: {base.categorize_fn_code}")
                print("-" * 50)

        Terminal.read_key()

    def register_base(self):
        Terminal.clear()
        print("=== Registro de Nova Base ===\n")

        name = Terminal.read_string("Nome da base: ", clear=False)
        path = Terminal.read_string("Caminho do arquivo CSV: ", clear=False)
        encoding = Terminal.read_string("Encoding [utf-8]: ", default="utf-8", clear=False)
        delimiter = Terminal.read_string("Delimitador [,]: ", default=",", clear=False)

        try:
            columns = read_csv_columns(path, encoding, delimiter)
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            Terminal.read_key()
            return

        colunas_str = show_columns(columns)
        input_indexes = Terminal.read_string(f"{colunas_str}\n\nÍndices das colunas de entrada: ", clear=False)
        exit_indexes = Terminal.read_string(f"{colunas_str}\nÍndices das colunas de saída: ", clear=False)

        input_columns = get_selected_indices(input_indexes, columns)
        exit_columns = get_selected_indices(exit_indexes, columns)

        base = BaseCsv()
        base.name = name
        base.path = path
        base.encoding = encoding
        base.delimiter = delimiter
        base.all_columns = columns
        base.input_columns = input_columns
        base.exit_columns = exit_columns

        # NOVO BLOCO: Estratégia de preenchimento
        fillna_strategy = {}
        for col in input_columns:
            Terminal.clear()
            coluna_entrada = f"Coluna de entrada: {col}\n"
            coluna_message = coluna_entrada
            coluna_message += "Deseja definir estratégia de preenchimento para nulos? (s/n): "
            usar_estrategia = Terminal.read_string(coluna_message, default="n")
            if usar_estrategia.lower() == 's':
                tipo = Terminal.read_string(
                    coluna_message + "Tipo de estratégia ('zero', 'mediana', 'media', 'outros', ou função lambda): ",)
                if tipo in ['zero', 'mediana', 'media', 'outros']:
                    fillna_strategy[col] = tipo
                elif tipo.startswith("lambda"):
                    try:
                        fillna_strategy[col] = eval(tipo, {"__builtins__": {}})
                    except Exception as e:
                        print(f"Função inválida: {e}")
                        Terminal.read_key()
        base.fillna_strategy = fillna_strategy

        try:
            df = pd.read_csv(path, encoding=encoding, sep=delimiter)
            col_saida = exit_columns[0]
            func_code, func = tentar_capturar_categorizador(df, col_saida)
            base.categorize_fn_code = func_code
            base.categorize_fn = func
        except Exception as e:
            print(f"Erro ao processar categorização: {e}")
            Terminal.read_key()

        self.bases.append(base)
        JsonExtension.save(self.path, self.bases)
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

        idx = Terminal.read_number("\nSelecione o índice da base a atualizar: ", clear=False)
        if not (0 <= idx < len(self.bases)):
            print("Índice inválido.")
            Terminal.read_key()
            return

        base = self.bases[idx]
        base.name = Terminal.read_string(f"Nome [{base.name}]: ", default=base.name, clear=False)
        base.path = Terminal.read_string(f"Caminho [{base.path}]: ", default=base.path, clear=False)
        base.encoding = Terminal.read_string(f"Encoding [{base.encoding or 'utf-8'}]: ",
                                             default=base.encoding or "utf-8", clear=False)
        base.delimiter = Terminal.read_string(f"Delimitador [{base.delimiter or ','}]: ", default=base.delimiter or ",",
                                              clear=False)

        try:
            columns = read_csv_columns(base.path, base.encoding, base.delimiter)
            base.all_columns = columns
        except Exception as e:
            print(f"Erro ao reler as colunas do CSV: {e}")
            Terminal.read_key()
            return

        colunas_str = show_columns(columns)
        input_indexes = Terminal.read_string(
            f"{colunas_str}\n\nColunas de entrada atuais: {', '.join(base.input_columns)}\nÍndices das colunas de entrada: ",
            default=','.join(map(str, [columns.index(c) for c in base.input_columns])), clear=False)

        Terminal.clear()

        exit_indexes = Terminal.read_string(
            f"{colunas_str}\nColunas de saída atuais: {', '.join(base.exit_columns)}\nÍndices das colunas de saída: ",
            default=','.join(map(str, [columns.index(c) for c in base.exit_columns])), clear=False)

        base.input_columns = get_selected_indices_safe(input_indexes, columns, base.input_columns)
        base.exit_columns = get_selected_indices_safe(exit_indexes, columns, base.exit_columns)

        # NOVO BLOCO: Estratégia de preenchimento
        fillna_strategy = {}
        for col in base.input_columns:
            Terminal.clear()
            coluna_entrada = f"Coluna de entrada: {col}\n"
            coluna_message = coluna_entrada
            coluna_message += "Deseja atualizar estratégia de preenchimento para nulos? (s/n): "
            usar_estrategia = Terminal.read_string(coluna_message, default="n")
            if usar_estrategia.lower() == 's':
                tipo = Terminal.read_string(
                    coluna_entrada + "Tipo de estratégia ('zero', 'mediana', 'media', 'outros', ou função lambda): ")
                if tipo in ['zero', 'mediana', 'media', 'outros']:
                    fillna_strategy[col] = tipo
                elif tipo.startswith("lambda"):
                    try:
                        fillna_strategy[col] = eval(tipo, {"__builtins__": {}})
                    except Exception as e:
                        print(f"Função inválida: {e}")
                        Terminal.read_key()
        base.fillna_strategy = fillna_strategy

        try:
            df = pd.read_csv(base.path, encoding=base.encoding, sep=base.delimiter)
            col_saida = base.exit_columns[0]
            func_code, func = tentar_capturar_categorizador(df, col_saida)
            base.categorize_fn_code = func_code
            base.categorize_fn = func
        except Exception as e:
            print(f"Erro ao processar categorização: {e}")
            Terminal.read_key()

        JsonExtension.save(self.path, self.bases)
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

        idx = Terminal.read_number("\nSelecione o índice da base a remover: ", clear=False)
        if not (0 <= idx < len(self.bases)):
            print("Índice inválido.")
            Terminal.read_key()
            return

        nome = self.bases[idx].name
        confirm = Terminal.read_string(f"Tem certeza que deseja remover '{nome}'? (s/n): ", clear=False)

        if confirm.lower() == 's':
            self.bases.pop(idx)
            JsonExtension.save(self.path, self.bases)
            print("Base removida com sucesso!")
        else:
            print("Operação cancelada.")

        Terminal.read_key()
