import json
from domain import BaseCsv


class JsonExtension:
    json_file: dict[str, str | None] = None

    @staticmethod
    def load(path: str) -> list[BaseCsv]:
        with open(path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        return [BaseCsv.from_json(item) for item in raw_data]

    @staticmethod
    def save(path: str, data: list[BaseCsv]):
        json_data = [item.to_json() for item in data]
        with open(path, 'w', encoding='utf-8') as f:
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
