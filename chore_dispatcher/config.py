from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for older runtimes
    import tomli as tomllib  # type: ignore


DEFAULT_CONFIG_PATH = Path("configs") / "default.toml"


@dataclass(frozen=True)
class Config:
    node_id: int = 0
    store_root: str = "../skips_chores"
    tmux_session: str = "chore-dispatcher"
    signal_dir: str = "/tmp/kiro_signals"

    auto_advance_plan_seconds: int = 5
    auto_advance_work_seconds: int = 10
    auto_advance_plan_review_seconds: int = 3
    auto_advance_work_review_seconds: int = 5

    default_log_level: str = "INFO"

    active_store_path: str = "data/active_chores.jsonl"
    archive_store_path: str = "data/archive_chores.jsonl"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in fields}
        return cls(**filtered)


def load_config(path: str | Path | None = None) -> Config:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with config_path.open("rb") as fh:
        data = tomllib.load(fh)

    return Config.from_dict(data)
