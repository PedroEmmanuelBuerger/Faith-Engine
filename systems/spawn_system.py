"""
Spawn de inimigos nas bordas do mundo, fora da vista da câmara.
Pressão aumenta quantidade e variedade — não HP/dano base por tempo.
"""

from __future__ import annotations

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
    cx, cy = state.camera_x, state.camera_y
    vw, vh = config.VIEWPORT_W, config.VIEWPORT_H
    m = 100.0
    left, right = cx - m, cx + vw + m
    top, bottom = cy - m, cy + vh + m

    zone = random.randint(0, 7)
    if zone == 0:
        return random.uniform(0, config.WORLD_W), random.uniform(0, max(0, top))
    if zone == 1:
        return random.uniform(0, config.WORLD_W), random.uniform(min(config.WORLD_H, bottom), config.WORLD_H)
    if zone == 2:
        return random.uniform(0, max(0, left)), random.uniform(0, config.WORLD_H)
    if zone == 3:
        return random.uniform(min(config.WORLD_W, right), config.WORLD_W), random.uniform(0, config.WORLD_H)
    return random.uniform(0, config.WORLD_W), random.choice(
        [random.uniform(0, 80), random.uniform(config.WORLD_H - 80, config.WORLD_H)]
    )


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

    x = max(radius, min(config.WORLD_W - radius, x))
    y = max(radius, min(config.WORLD_H - radius, y))

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
        _spawn_one(state)
