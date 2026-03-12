import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

from extensions import JsonExtension, Terminal, preprocessor_base
from domain import BaseCsv
from pages import ListablePage, BasePage


class SvmSemPipelinePage(ListablePage, BasePage):
    def __init__(self, path: str):
        super().__init__()
        self.base_treinada = None
        self.raw_df = None
        self.bases: list[BaseCsv] = JsonExtension.load(path)
        self.modelo = None
        self.X_test = None
        self.y_test = None
        self.feature_names = []

        self.opcoes = {
            **{i: (base.name, lambda b=base: self.processar_base(b)) for i, base in enumerate(self.bases)},
            len(self.bases): ('Sair', lambda: None)
        }

    def processar_base(self, base: BaseCsv):
        Terminal.clear()
        print(f"Treinando modelo para base: {base.name}\n")

        try:
            X, y = preprocessor_base(base)

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)

            clf = SVC(gamma='auto')
            clf.fit(X_train, y_train)

            self.modelo = clf
            self.X_test = X_test
            self.y_test = y_test
            self.feature_names = X.columns.tolist()

            print("\nModelo treinado com sucesso!\n")

            Terminal.read_key()
            self.base_treinada = base
            self.raw_df = pd.read_csv(base.path, encoding=base.encoding, sep=base.delimiter)
            self.mostrar_menu_apos_treino()

        except Exception as e:
            print(f"Erro ao processar base: {e}")
            Terminal.read_key()

    def mostrar_menu_apos_treino(self):
        while True:
            Terminal.clear()
            opcoes = ''
            opcoes += '=== Modelo Treinado (SVM) ===\n'
            opcoes += "1 - Mostrar acurácia\n"
            opcoes += "2 - Realizar predição\n"
            opcoes += "4 - Voltar\n\n"
            opcoes += "Escolha uma opção: "

            op = Terminal.read_number(opcoes)

            if op == 1:
                y_pred = self.modelo.predict(self.X_test)
                accuracy = accuracy_score(self.y_test, y_pred)
                print(f"\nAcurácia: {accuracy * 100:.2f}%")
                Terminal.read_key()

            elif op == 2:
                base = self.base_treinada
                input_data = {}

                for col in base.input_columns:
                    val = Terminal.read_string(f"{col}: ")
                    input_data[col] = [val]

                df_input = pd.DataFrame(input_data)

                for col in df_input.columns:
                    if col in self.raw_df.columns:
                        tipo = self.raw_df[col].dtype
                        try:
                            df_input[col] = df_input[col].astype(tipo)
                        except Exception:
                            pass

                temp_base = BaseCsv()
                temp_base.path = base.path
                temp_base.encoding = base.encoding
                temp_base.delimiter = base.delimiter
                temp_base.input_columns = base.input_columns
                temp_base.exit_columns = base.exit_columns
                temp_base.categorize_fn = base.categorize_fn
                temp_base.categorize_fn_code = base.categorize_fn_code
                df_processado, _ = preprocessor_base(temp_base, df_default=df_input)
                df_processado = df_processado.reindex(columns=self.feature_names, fill_value=0)

                resultado = self.modelo.predict(df_processado)[0]
                print(f"\nClasse prevista: {resultado}")
                Terminal.read_key()

            elif op == 3:
                break
            else:
                print("Opção inválida.")
                Terminal.read_key()
