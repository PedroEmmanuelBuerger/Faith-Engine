"""
Pickups no mundo: sistema genérico + Bíblia (abre escolha de upgrades).
"""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, Any, Dict, List

from core import sfx
from effects import particles as particle_fx
from entities.pickup import PICKUP_BIBLE
from systems import upgrade_system

if TYPE_CHECKING:
    from core.game_state import GameState


def _spawn_position(state: GameState) -> tuple[float, float]:
    p = state.player
    for _ in range(12):
        ang = random.uniform(0, math.tau)
        d = random.uniform(200.0, 480.0)
        x = p.x + math.cos(ang) * d
        y = p.y + math.sin(ang) * d
        return x, y
    return p.x + 280, p.y


def try_spawn_bibles(state: GameState, dt: float) -> None:
    if state.level_up_paused or state.game_paused or state.death_mode != "alive":
        return
    state.bible_spawn_timer -= dt
    if state.bible_spawn_timer > 0:
        return
    state.bible_spawn_timer = random.uniform(32.0, 58.0)
    x, y = _spawn_position(state)
    state.pickups.append(
        {
            "kind": PICKUP_BIBLE,
            "x": x,
            "y": y,
            "r": 16.0,
            "pulse": 0.0,
        }
    )


def _collect(state: GameState, pu: Dict[str, Any]) -> None:
    kind = pu["kind"]
    if kind == PICKUP_BIBLE:
        particle_fx.spawn_bible_collect(state, pu["x"], pu["y"])
        sfx.play_shoot()
        state.screen_shake = max(state.screen_shake, 3.5)
        if not state.level_up_paused:
            state.level_up_paused = True
            state.upgrade_choice_ids = upgrade_system.random_choices(3)


def _player_touches(pu: Dict[str, Any], px: float, py: float, pr: float) -> bool:
    dx = pu["x"] - px
    dy = pu["y"] - py
    return math.hypot(dx, dy) <= pr + pu["r"]


def update(state: GameState, dt: float) -> None:
    try_spawn_bibles(state, dt)
    if state.game_paused or state.death_mode != "alive":
        return
    p = state.player
    collecting = not state.level_up_paused
    alive: List[Dict[str, Any]] = []
    for pu in state.pickups:
        pu["pulse"] = pu.get("pulse", 0.0) + dt * 3.2
        if collecting and _player_touches(pu, p.x, p.y, p.radius):
            _collect(state, pu)
        else:
            alive.append(pu)
    state.pickups = alive
