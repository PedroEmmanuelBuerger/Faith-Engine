"""Atalhos para efeitos sonoros (ligado em runtime ao AudioManager)."""

from __future__ import annotations

import time
from typing import Any, Optional

_mgr: Optional[Any] = None
_last_hit_t = 0.0
_HIT_GAP = 0.085
_last_enemy_death_t = 0.0
_ED_GAP = 0.045


def bind(manager: Any) -> None:
    global _mgr
    _mgr = manager


def set_music_intensity(intensity: float) -> None:
    if _mgr and hasattr(_mgr, "set_intensity_volume"):
        _mgr.set_intensity_volume(intensity)


def play_shoot() -> None:
    if _mgr:
        _mgr.play_shoot()


def play_shoot_heavy() -> None:
    if _mgr and hasattr(_mgr, "play_shoot_heavy"):
        _mgr.play_shoot_heavy()
    elif _mgr:
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


def play_pickup() -> None:
    if _mgr and hasattr(_mgr, "play_pickup"):
        _mgr.play_pickup()
    elif _mgr:
        _mgr.play_shoot()


def play_enemy_death() -> None:
    global _last_enemy_death_t
    if not _mgr:
        return
    now = time.monotonic()
    if now - _last_enemy_death_t < _ED_GAP:
        return
    _last_enemy_death_t = now
    if hasattr(_mgr, "play_enemy_death"):
        _mgr.play_enemy_death()
    else:
        _mgr.play_hit()
