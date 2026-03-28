"""Atalhos para efeitos sonoros (ligado em runtime ao AudioManager)."""

from __future__ import annotations

import time
from typing import Any, Optional

_mgr: Optional[Any] = None
_last_hit_t = 0.0
_HIT_GAP = 0.085


def bind(manager: Any) -> None:
    global _mgr
    _mgr = manager


def play_shoot() -> None:
    if _mgr:
        _mgr.play_shoot()


def play_hit() -> None:
    global _last_hit_t
    if not _mgr:
        return
    now = time.monotonic()
    if now - _last_hit_t < _HIT_GAP:
        return
    _last_hit_t = now
    _mgr.play_hit()


def play_death() -> None:
    if _mgr:
        _mgr.play_death()
