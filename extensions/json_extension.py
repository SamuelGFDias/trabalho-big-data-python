import json
from domain import BaseCsv


class JsonExtension:
    json_file: dict[str, str | None] = None

    @staticmethod
    def load(path: str) -> list[BaseCsv]:
        with open(path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        bases = []
        for item in raw_data:
            base = BaseCsv()
            base.name = item['name']
            base.path = item['path']
            base.encoding = item['encoding']
            base.delimiter = item['delimiter']
            base.all_columns = item['all_columns']
            base.input_columns = item['input_columns']
            base.exit_columns = item['exit_columns']
            base.categorize_fn_code = item.get('categorize_fn_code')

            if base.categorize_fn_code:
                try:
                    base.categorize_fn = eval(base.categorize_fn_code, {"__builtins__": {}})
                except Exception as e:
                    print(f"[ERRO] Não foi possível interpretar categorize_fn: {e}")
                    base.categorize_fn = None

            bases.append(base)
        return bases

    @staticmethod
    def save(path: str, data: list):
        json_data = [item.to_json() for item in data]
        with open(path, 'w', encoding='utf-8') as f:
            import json
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def get(key: str) -> str:
        return JsonExtension.json_file[key]

    @staticmethod
    def set(key: str, value: str) -> None:
        JsonExtension.json_file[key] = value

        with open(JsonExtension.json_file['path'], 'w') as file:
            json.dump(JsonExtension.json_file, file)

    @staticmethod
    def delete(key: str) -> None:
        del JsonExtension.json_file[key]

        with open(JsonExtension.json_file['path'], 'w') as file:
            json.dump(JsonExtension.json_file, file)

    @staticmethod
    def clear():
        JsonExtension.json_file = None
