from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import requests

from src.config import AppConfig
from src.utils.io import read_json, write_json
from src.utils.logging import get_logger

logger = get_logger(__name__)


class SharedStateStore:
    def __init__(self, settings: AppConfig) -> None:
        self.settings = settings
        self.local_dir = settings.state_dir / "shared"
        self.local_dir.mkdir(parents=True, exist_ok=True)

    def read_json(self, name: str, default: Any = None) -> Any:
        if self.settings.shared_state.github_repo:
            payload = self._read_remote(name)
            if payload is not None:
                self._write_local(name, payload)
                return payload
        return read_json(self.local_dir / f"{name}.json", default)

    def write_json(self, name: str, payload: Any) -> None:
        self._write_local(name, payload)
        if self.settings.shared_state.github_repo and self.settings.shared_state.github_token:
            self._write_remote(name, payload)

    def _write_local(self, name: str, payload: Any) -> None:
        write_json(self.local_dir / f"{name}.json", payload)

    def _read_remote(self, name: str) -> Any | None:
        repo = self.settings.shared_state.github_repo
        branch = self.settings.shared_state.github_branch
        state_dir = self.settings.shared_state.github_state_dir.strip("/")
        raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{state_dir}/{name}.json"
        try:
            response = requests.get(raw_url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as exc:  # pragma: no cover
            logger.warning("Shared state remote read failed: %s", exc)
        return None

    def _write_remote(self, name: str, payload: Any) -> None:
        repo = self.settings.shared_state.github_repo
        branch = self.settings.shared_state.github_branch
        state_dir = self.settings.shared_state.github_state_dir.strip("/")
        path = f"{state_dir}/{name}.json"
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {self.settings.shared_state.github_token}",
            "Accept": "application/vnd.github+json",
        }
        content = (self.local_dir / f"{name}.json").read_text()
        sha = None
        try:
            existing = requests.get(f"{url}?ref={branch}", headers=headers, timeout=10)
            if existing.status_code == 200:
                sha = existing.json().get("sha")
        except Exception:
            sha = None
        body = {
            "message": f"Update shared state: {name}",
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "branch": branch,
        }
        if sha:
            body["sha"] = sha
        try:
            response = requests.put(url, headers=headers, json=body, timeout=20)
            response.raise_for_status()
        except Exception as exc:  # pragma: no cover
            logger.warning("Shared state remote write failed: %s", exc)
