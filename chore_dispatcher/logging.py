from __future__ import annotations

import logging


DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(level: str) -> None:
    logging.basicConfig(level=level.upper(), format=DEFAULT_LOG_FORMAT)
