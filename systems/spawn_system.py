"""
Spawn em anel à volta do jogador (mapa infinito).
"""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from core import config
from entities.enemy import Enemy, EnemyKind, stats_for_kind

if TYPE_CHECKING:
    from core.game_state import GameState

_KINDS = (
    EnemyKind.CORRUPT_PRIEST,
    EnemyKind.SHADOW_CREATURE,
    EnemyKind.POSSESSED_STATUE,
    EnemyKind.SKITTER,
    EnemyKind.BULWARK,
    EnemyKind.HERETIC,
    EnemyKind.CARRION_BOMB,
)

_WEIGHTS = (0.22, 0.18, 0.12, 0.18, 0.08, 0.12, 0.10)


def _random_point_outside_view(state: GameState) -> tuple[float, float]:
    px, py = state.player.x, state.player.y
    vw, vh = config.VIEWPORT_W, config.VIEWPORT_H
    margin = 80.0
    inner = max(vw, vh) / 2 + margin
    outer = inner + 420 + random.uniform(0, 380)
    ang = random.uniform(0, math.tau)
    d = random.uniform(inner, outer)
    return px + math.cos(ang) * d, py + math.sin(ang) * d


def _trim_excess_enemies(state: GameState) -> None:
    cap = config.MAX_ENEMIES_ALIVE
    if len(state.enemies) <= cap:
        return
    px, py = state.player.x, state.player.y
    state.enemies.sort(
        key=lambda e: (e.x - px) ** 2 + (e.y - py) ** 2,
        reverse=True,
    )
    del state.enemies[cap:]


def _spawn_one(state: GameState) -> None:
    x, y = _random_point_outside_view(state)
    kind = random.choices(_KINDS, weights=_WEIGHTS, k=1)[0]

    base_hp = 24.0
    base_spd = 58.0
    base_dmg = 7.0
    base_xp = 7.0

    hp, spd, dmg, xp, radius = stats_for_kind(kind, base_hp, base_spd, base_dmg, base_xp)

    explodes = kind == EnemyKind.CARRION_BOMB
    is_ranged = kind == EnemyKind.HERETIC

    state.enemies.append(
        Enemy(
            x,
            y,
            max_hp=hp,
            speed=spd,
            damage=dmg,
            radius=radius,
            xp_value=xp,
            kind=kind,
            explodes=explodes,
            is_ranged=is_ranged,
        )
    )


def spawn_enemy(state: GameState) -> None:
    pressure = state.spawn_pressure
    count = 1
    extra = int((pressure - 1.0) * 0.72)
    count += min(3, max(0, extra))
    if state.wave >= 4 and random.random() < 0.18:
        count += 1
    if state.wave >= 10 and random.random() < 0.1:
        count += 1

    for _ in range(count):
        if len(state.enemies) >= config.MAX_ENEMIES_ALIVE:
            break
        _spawn_one(state)
    _trim_excess_enemies(state)
