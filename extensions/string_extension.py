def isnullorempty(s: str | None) -> bool:
    return s is None or len(s.strip()) == 0
