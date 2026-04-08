from pathlib import Path

_JSON_FILES = ["items.json", "users.json"]  # FIXME хардкод!


def ensure_json_storage(data_dir: str) -> None:
    """Create data directory and seed empty JSON files if missing.

    Analogous to DB migrations: must run once at startup,
    before any repository is instantiated.
    """
    base = Path(data_dir)
    base.mkdir(parents=True, exist_ok=True)
    for name in _JSON_FILES:
        path = base / name
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
