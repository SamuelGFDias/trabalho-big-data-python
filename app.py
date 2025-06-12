import sys
from time import sleep
from typing import Callable

import pandas as pd
import numpy as np
from sklearn import tree
from matplotlib import pyplot as plt

from extensions import Terminal, normalize_string
from models.DataInfo import DataInfo
from services import DecisionTreeService, SVMService


def sair(message: str) -> Callable[[], None]:
    def exit_system():
        print(message, end='', flush=True)
        for _ in range(3):
            sleep(0.5)
            print('.', end='', flush=True)
        print()
        sys.exit()

    return exit_system


def pre_processar(df: pd.DataFrame) -> pd.DataFrame:
    # Datas
    df['data_criacao'] = pd.to_datetime(df['data_criacao'], format='%d/%m/%Y')
    df['data_limite'] = pd.to_datetime(df['data_limite'], format='%d/%m/%Y')
    df['dias_experados'] = (df['data_limite'] - df['data_criacao']).dt.days

    # Feature engineering temporal
    df['mes_criacao'] = df['data_criacao'].dt.month
    df['dia_semana_criacao'] = df['data_criacao'].dt.weekday

    # Estatísticas por cidade
    media_cidade = df.groupby('cidade')['dias_experados'].transform('mean')
    df['media_dias_cidade'] = media_cidade
    df['desvio_dias'] = df['dias_experados'] - media_cidade
    
    # Ciclicalidade para projeção de períodos cíclicos como (dias da semana e meses do ano)
    df['mes_sin'] = np.sin(2 * np.pi * df['mes_criacao'] / 12)
    df['mes_cos'] = np.cos(2 * np.pi * df['mes_criacao'] / 12)
    df['dia_sin'] = np.sin(2 * np.pi * df['dia_semana_criacao'] / 7)
    df['dia_cos'] = np.cos(2 * np.pi * df['dia_semana_criacao'] / 7)

    # Limpar colunas originais
    df = df.drop(columns=[
        'data_criacao', 'data_limite',
        'mes_criacao', 'dia_semana_criacao',
    ])

    # Verifico se a coluna de sáida está, e se estiver, eu excluo. (Pois essa função é usada para processar a base e a amostra que não contém a coluna de saída)
    if ('dias_para_entrega' in df.columns):
        df['status_entrega'] = df['dias_para_entrega'].apply(lambda x: 'rápido' if x <= 7 else 'lento')
        df = df.drop(columns=['dias_para_entrega'])

    return df


def obter_amostra_usuario(template_df: pd.DataFrame) -> pd.DataFrame:
    # Solicita dados crus ao usuário com base nas colunas originais
    entrada = {}
    for col in DataInfo.raw_columns:
        if col in ['dias_para_entrega', '']:  # não solicitar dias calculados
            continue
        if col in DataInfo.unique_values:
            while (True):
                Terminal.clear()
                validos = DataInfo.unique_values[col]
                print()
                valor = Terminal.read_string(f"Valores válidos para '{col}': {validos}\nInforme '{col}': ", clear=True)

                if (valor not in validos):
                    Terminal.read_key("Valor inválido informado.")
                else:
                    entrada[col] = normalize_string(valor.strip().replace(' ', '_'))
                    break
        else:
            valor = Terminal.read_string(f"Informe '{col}': ", clear=False)
            entrada[col] = valor.strip()

    df_input = pd.DataFrame([entrada])
    # Normaliza nomes antes de preprocessar
    df_input['cidade'] = normalize_string(df_input['cidade'].replace(' ', '_'))
    df_input['regiao'] = normalize_string(df_input['regiao'].replace(' ', '_'))

    # Processa com mesmas regras do treino
    df_input = pre_processar(df_input)

    # One-hot encoding para categóricas originais
    df_input = pd.get_dummies(
        df_input,
        columns=['cidade', 'regiao'],
        drop_first=True,
        dtype=int
    )
    # Alinha colunas com template
    features = template_df.drop(columns=['status_entrega']).columns
    df_input = df_input.reindex(columns=features, fill_value=0)
    return df_input


def exibir_menu_classificador(
        nome: str,
        service,
        df: pd.DataFrame,
        show_tree: bool = False
):
    X = df.drop(columns=['status_entrega'])
    y = df['status_entrega']
    service.train(X, y)

    while True:
        Terminal.clear()
        print(f"{nome}")
        print("1 - Mostrar acurácia")
        if show_tree:
            print("2 - Exibir gráfico da árvore")
            print("3 - Classificar nova amostra")
            print("0 - Voltar")
        else:
            print("2 - Classificar nova amostra")
            print("0 - Voltar")

        opc = Terminal.read_number("Selecione uma opção:", clear=False)

        if opc == 1:
            acc = service.predict()
            print(f"Acurácia de {nome}: {acc * 100:.2f}%")

        elif opc == 2 and show_tree:
            clf = service.model
            plt.figure(figsize=(20, 10))
            tree.plot_tree(clf, feature_names=X.columns.tolist(),
                           class_names=y.astype(str).unique().tolist(), filled=True)
            plt.title(f"Árvore de Decisão - {nome}")
            plt.show()
            print("Árvore exibida.")

        elif (opc == 3 and show_tree) or (opc == 2 and not show_tree):
            df_input = obter_amostra_usuario(df)
            pred = service.model.predict(df_input)
            print(f"Classe prevista: {pred[0]}")

        elif opc == 0:
            break
        else:
            print("Opção inválida.")

        Terminal.read_key()

def show_menu(df: pd.DataFrame):
    opcoes = {
        1: ('Árvore de Decisão', lambda: exibir_menu_classificador(
            'Árvore de Decisão', DecisionTreeService(), df, show_tree=True
        )),
        2: ('SVM', lambda: exibir_menu_classificador(
            'SVM', SVMService(pipeline=False), df, show_tree=False
        )),
        -1: ('Sair', sair("Bye Bye")),
    }

    while True:
        Terminal.clear()
        print("*********** BIG DATA ANALYTICS *********\n")
        for k, v in opcoes.items():
            print(f"{k} - {v[0]}")

        opc = Terminal.read_number("Selecione uma opção:", clear=False)
        if opc in opcoes:
            opcoes[opc][1]()
            if opc == -1:
                break
        else:
            print("Opção inválida.")
            Terminal.read_key()


def main():
    df = pd.read_csv('assets/base_entregas_suprimentos.txt', sep=',')
    df.columns = df.columns.str.strip().str.replace(' ', '_').map(normalize_string)

    DataInfo.feature_columns = [
        col for col in df.columns if col != 'dias_para_entrega'
    ]

    DataInfo.raw_columns = df.columns.tolist()

    df = pre_processar(df)

    df['cidade'] = df['cidade'].str.strip().str.replace(' ', '_').map(normalize_string)
    df['regiao'] = df['regiao'].str.strip().str.replace(' ', '_').map(normalize_string)

    DataInfo.columns = df.columns.tolist()
    DataInfo.unique_values = {
        col: df[col].unique().tolist()
        for col in df.columns
        if df[col].dtype == 'object' and col != 'status_entrega'
    }

    df = pd.get_dummies(
        df,
        columns=list(DataInfo.unique_values.keys()),
        drop_first=True,
        dtype=int
    )
    show_menu(df)


if __name__ == '__main__':
    main()
