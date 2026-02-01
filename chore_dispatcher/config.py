from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for older runtimes
    import tomli as tomllib  # type: ignore


_MODULE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = _MODULE_ROOT / "configs" / "default.toml"


@dataclass(frozen=True)
class Config:
    node_id: int = 0
    store_root: str = "../skips_chores"
    tmux_session: str = "chore-dispatcher"
    tmux_enabled: bool = True
    signal_dir: str = "/tmp/kiro_signals"
    http_host: str = "127.0.0.1"
    http_port: int = 8080
    mcp_path: str = "/mcp"
    kiro_command: str = "/Applications/Kiro CLI.app/Contents/MacOS/kiro-cli chat --trust-tools @chore-dispatcher,read,write,web_fetch,web_search,grep,glob,shell,code"

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
    if path is not None:
        config_path = Path(path)
    else:
        config_path = DEFAULT_CONFIG_PATH
        if not config_path.exists():
            config_path = Path("configs") / "default.toml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with config_path.open("rb") as fh:
        data = tomllib.load(fh)

    return Config.from_dict(data)
