from __future__ import annotations

import argparse
import sys
from importlib import metadata

from chore_dispatcher.config import load_config
from chore_dispatcher.logging import setup_logging


def _get_version() -> str:
    try:
        return metadata.version("chore-dispatcher")
    except metadata.PackageNotFoundError:
        return "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chore-dispatcher")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("--health", action="store_true", help="Run a basic health check")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(_get_version())
        return 0

    if args.health:
        config = load_config(args.config)
        setup_logging(config.default_log_level)
        print("ok")
        return 0

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
