from __future__ import annotations

from datetime import datetime, timedelta

from src.config import AppConfig, get_settings
from src.state.store import SharedStateStore
from src.utils.io import read_json


def get_store(settings: AppConfig | None = None) -> SharedStateStore:
    return SharedStateStore(settings or get_settings())


def read_shared_json(name: str, default):
    settings = get_settings()
    path = settings.state_dir / "shared" / f"{name}.json"
    store = get_store(settings)
    return store.read_json(name, read_json(path, default))


def sample_timestamp(minutes_ago: int = 0) -> str:
    return (datetime.now() - timedelta(minutes=minutes_ago)).isoformat()
