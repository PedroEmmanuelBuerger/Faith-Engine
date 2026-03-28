"""
Logging para depuração: logs/game.log e logs/errors.log.
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOG_DIR = os.path.join(_ROOT, "logs")
_CONFIGURED = False


def _ensure_dir() -> None:
    os.makedirs(_LOG_DIR, exist_ok=True)


def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    _ensure_dir()
    game_path = os.path.join(_LOG_DIR, "game.log")
    err_path = os.path.join(_LOG_DIR, "errors.log")

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fh = RotatingFileHandler(
        game_path, maxBytes=512_000, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    eh = RotatingFileHandler(
        err_path, maxBytes=256_000, backupCount=3, encoding="utf-8"
    )
    eh.setLevel(logging.WARNING)
    eh.setFormatter(fmt)

    root.handlers.clear()
    root.addHandler(fh)
    root.addHandler(eh)

    logging.captureWarnings(True)
    _CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or "culto")


def log_state(message: str) -> None:
    get_logger("state").info(message)
