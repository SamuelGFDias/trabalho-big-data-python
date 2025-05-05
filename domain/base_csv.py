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
        self.categorize_fn_code: str | None = None  # string serializada do lambda
        self.categorize_fn: Callable[[float], str] | None = None

    def to_json(self):
        return {
            'name': self.name,
            'path': self.path,
            'encoding': self.encoding,
            'delimiter': self.delimiter,
            'all_columns': self.all_columns,
            'input_columns': self.input_columns,
            'exit_columns': self.exit_columns,
            "categorize_fn_code": self.categorize_fn_code
        }
