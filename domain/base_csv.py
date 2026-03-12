from typing import Callable


class BaseCsv:
    def __init__(self):
        self.name = None
        self.path = None
        self.encoding = None
        self.delimiter = None
        self.all_columns = None
        self.input_columns = None
        self.exit_columns = None
        self.categorize_fn_code: str | None = None
        self.categorize_fn: Callable[[float], str] | None = None
        self.fillna_strategy: dict[str, str | float | Callable] = {}

    def to_json(self):
        serialized_strategy = {}
        for k, v in self.fillna_strategy.items():
            if callable(v):
                serialized_strategy[k] = v.__name__ if v.__name__ != "<lambda>" else "lambda"
            else:
                serialized_strategy[k] = v

        return {
            'name': self.name,
            'path': self.path,
            'encoding': self.encoding,
            'delimiter': self.delimiter,
            'all_columns': self.all_columns,
            'input_columns': self.input_columns,
            'exit_columns': self.exit_columns,
            "categorize_fn_code": self.categorize_fn_code,
            "fillna_strategy": serialized_strategy
        }

    @staticmethod
    def from_json(data: dict):
        base = BaseCsv()
        base.name = data.get('name')
        base.path = data.get('path')
        base.encoding = data.get('encoding')
        base.delimiter = data.get('delimiter')
        base.all_columns = data.get('all_columns')
        base.input_columns = data.get('input_columns')
        base.exit_columns = data.get('exit_columns')
        base.categorize_fn_code = data.get("categorize_fn_code")

        if base.categorize_fn_code:
            try:
                base.categorize_fn = eval(base.categorize_fn_code, {"__builtins__": {}})
            except Exception:
                base.categorize_fn = None

        strategy = data.get("fillna_strategy", {})
        for k, v in strategy.items():
            if isinstance(v, str) and v.strip().startswith("lambda"):
                try:
                    strategy[k] = eval(v, {"__builtins__": {}})
                except Exception:
                    strategy[k] = "outros"
        base.fillna_strategy = strategy

        return base
