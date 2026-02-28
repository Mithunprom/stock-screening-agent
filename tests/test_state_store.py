from src.config import get_settings
from src.state.store import SharedStateStore


def test_shared_state_store_local_roundtrip(tmp_path) -> None:
    settings = get_settings()
    settings.state_dir = tmp_path
    settings.cache_dir = tmp_path / "cache"
    settings.shared_state.github_repo = ""
    settings.ensure_dirs()

    store = SharedStateStore(settings)
    payload = {"hello": "world"}
    store.write_json("test_snapshot", payload)

    assert store.read_json("test_snapshot", {}) == payload
