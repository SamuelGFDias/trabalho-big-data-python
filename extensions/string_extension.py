import re
import unidecode

def is_null_or_empty(s: str | None) -> bool:
    return s is None or len(s.strip()) == 0

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)

def normalize_string(s: str) -> str:
    return unidecode.unidecode(str(s)).lower()

