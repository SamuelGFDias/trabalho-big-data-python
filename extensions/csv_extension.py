import csv
from pathlib import Path
from typing import Callable

import requests
import io
import pandas as pd
from domain import BaseCsv
from extensions.terminal import Terminal


def read_csv_columns(path: str, encoding: str, delimiter: str) -> list[str]:
    try:
        if path.startswith("http"):
            response = requests.get(path)
            response.raise_for_status()
            content = response.content.decode(encoding)
            csvfile = io.StringIO(content)
        else:
            if not Path(path).exists():
                raise FileNotFoundError("Arquivo local não encontrado.")
            csvfile = open(path, encoding=encoding, newline='')

        with csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            return next(reader)
    except Exception as e:
        raise RuntimeError(f"Erro ao ler o CSV: {e}")


def preprocessar_base(base: BaseCsv, df_default: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.Series]:
    df = df_default

    if df is None:
        df = pd.read_csv(base.path, encoding=base.encoding, sep=base.delimiter)

    # 1. Processar datas
    for col in df.columns:
        if "data" in col.lower():
            try:
                series = pd.to_datetime(df[col])
                df[f'dia_{col}'] = series.dt.day
                df[f'dia_semana_{col}'] = series.dt.dayofweek
                df[f'mes_{col}'] = series.dt.month
                df[f'ano_{col}'] = series.dt.year
                df.drop(columns=[col], inplace=True)
            except Exception:
                continue

    # 2. Preparar colunas de entrada
    input_cols = [c for c in df.columns if c not in base.exit_columns]
    input_df = df[input_cols].copy()

    for col in input_df.columns:
        if not pd.api.types.is_numeric_dtype(input_df[col]):
            input_df = pd.get_dummies(input_df, columns=[col])

    for col in input_df.columns:
        if input_df[col].dtype == 'bool':
            input_df[col] = input_df[col].astype(int)

    # 3. Processar saída
    target = base.exit_columns[0]
    if target in df.columns:
        y = df[target]

        if pd.api.types.is_numeric_dtype(y) and y.nunique() > 7:
            if base.categorize_fn:
                y = y.apply(base.categorize_fn)
            else:
                raise ValueError(
                    f"A coluna '{target}' possui {y.nunique()} valores únicos. "
                    f"Defina uma função 'categorize_fn' no BaseCsv correspondente."
                )
    else:
        y = None

    return input_df, y


def show_columns(columns: list[str]) -> str:
    return "\n".join([f"{i} - {col}" for i, col in enumerate(columns)])


def get_selected_indices(indices: str, columns: list[str]) -> list[str]:
    try:
        return [columns[int(i.strip())] for i in indices.split(',') if i.strip().isdigit()]
    except Exception:
        return []


def get_selected_indices_safe(indices: str, columns: list[str], original: list[str]) -> list[str]:
    try:
        return get_selected_indices(indices, columns)
    except Exception:
        return original


def tentar_capturar_categorizador(df: pd.DataFrame, col_saida: str) -> tuple[str | None, Callable | None]:
    if pd.api.types.is_numeric_dtype(df[col_saida]) and df[col_saida].nunique() > 7:
        Terminal.clear()
        print(f"\nA coluna de saída '{col_saida}' é numérica e possui muitos valores distintos.")
        print("Você precisa informar uma função de categorização (ex: lambda x: 'Alto' if x >= 5 else 'Baixo')")
        func_code = Terminal.read_string("Digite a função lambda: ", clear=False)
        try:
            func = eval(func_code, {"__builtins__": {}})
            _ = func(df[col_saida].dropna().iloc[0])
            return func_code, func
        except Exception as e:
            print(f"Função inválida: {e}")
            Terminal.read_key()
    return None, None
