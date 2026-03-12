import csv
from pathlib import Path
from typing import Callable
import re
import unidecode
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


import pandas as pd
import re
import unidecode
from domain import BaseCsv


def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)


def normalize_string(s: str) -> str:
    return unidecode.unidecode(str(s)).lower()

def apply_fillna_strategy(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    for col, rule in strategy.items():
        if col not in df.columns:
            continue

        if callable(rule):
            df[col] = rule(df[col])
        elif rule == "mediana":
            df[col] = df[col].fillna(df[col].median())
        elif rule == "media":
            df[col] = df[col].fillna(df[col].mean())
        elif rule == "zero":
            df[col] = df[col].fillna(0)
        elif isinstance(rule, str):
            df[col] = df[col].astype(str).replace(r'^\s*$', pd.NA, regex=True).fillna(rule)
        else:
            df[col] = df[col].fillna(rule)
    return df


def preprocessor_base(base: BaseCsv, df_default: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.Series]:
    df = df_default or pd.read_csv(base.path, encoding=base.encoding, sep=base.delimiter)

    # 1. Aplicar estratégias customizadas de preenchimento
    if hasattr(base, "fillna_strategy") and base.fillna_strategy:
        df = apply_fillna_strategy(df, base.fillna_strategy)

    # 2. Preencher valores faltantes nas colunas restantes
    for col in df.columns:
        if df[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df[col]):
            df[col] = df[col].replace(r'^\s*$', pd.NA, regex=True).fillna("outros")
            df[col] = df[col].astype(str).map(normalize_string)

        elif pd.api.types.is_numeric_dtype(df[col]):
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())

    # 3. Processar colunas datetime
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            series = df[col]
        else:
            try:
                series = pd.to_datetime(df[col])
            except Exception:
                continue

        df[f'dia_{col}'] = series.dt.day
        df[f'dia_semana_{col}'] = series.dt.dayofweek
        df[f'mes_{col}'] = series.dt.month
        df[f'ano_{col}'] = series.dt.year
        df.drop(columns=[col], inplace=True)

    # 4. Separar colunas de entrada
    input_cols = [c for c in df.columns if c not in base.exit_columns]
    input_df = df[input_cols].copy()

    # 5. Gerar dummies
    input_df = pd.get_dummies(input_df, drop_first=False)

    # 6. Converter booleanos para inteiros
    for col in input_df.select_dtypes(include='bool').columns:
        input_df[col] = input_df[col].astype(int)

    # 7. Sanitizar nomes de colunas
    input_df.columns = [sanitize_filename(c) for c in input_df.columns]

    # 8. Processar saída
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
        mensagem = ''
        mensagem += f"\nA coluna de saída '{col_saida}' é numérica e possui muitos valores distintos.\n"
        mensagem += "Você precisa informar uma função de categorização (ex: lambda x: 'Alto' if x >= 5 else 'Baixo')\n"
        mensagem += "Digite a função lambda: "

        func_code = Terminal.read_string(mensagem)
        try:
            func = eval(func_code, {"__builtins__": {}})
            _ = func(df[col_saida].dropna().iloc[0])
            return func_code, func
        except Exception as e:
            print(f"Função inválida: {e}")
            Terminal.read_key()
    return None, None
