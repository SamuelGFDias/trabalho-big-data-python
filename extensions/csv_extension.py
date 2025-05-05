import csv
from pathlib import Path

import requests
import io


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

