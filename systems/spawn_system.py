"""
Spawn de inimigos nas bordas do mundo, fora da vista da câmara.
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
    EnemyKind.POSSESSED_STATUE,
    EnemyKind.SHADOW_CREATURE,
)


def _random_point_outside_view(state: GameState) -> tuple[float, float]:
    """Ponto no mundo, fora do retângulo da câmara (com margem)."""
    cx, cy = state.camera_x, state.camera_y
    vw, vh = config.VIEWPORT_W, config.VIEWPORT_H
    m = 100.0
    left, right = cx - m, cx + vw + m
    top, bottom = cy - m, cy + vh + m

    # Escolhe uma “faixa” à volta do ecrã visível
    zone = random.randint(0, 7)
    if zone == 0:
        return random.uniform(0, config.WORLD_W), random.uniform(0, max(0, top))
    if zone == 1:
        return random.uniform(0, config.WORLD_W), random.uniform(min(config.WORLD_H, bottom), config.WORLD_H)
    if zone == 2:
        return random.uniform(0, max(0, left)), random.uniform(0, config.WORLD_H)
    if zone == 3:
        return random.uniform(min(config.WORLD_W, right), config.WORLD_W), random.uniform(0, config.WORLD_H)
    # cantos / bordas finas
    return random.uniform(0, config.WORLD_W), random.choice(
        [random.uniform(0, 80), random.uniform(config.WORLD_H - 80, config.WORLD_H)]
    )


def spawn_enemy(state: GameState) -> None:
    scale = 1.0 + (state.wave - 1) * 0.08
    diff = state.difficulty_mult
    x, y = _random_point_outside_view(state)

    kind = random.choices(
        _KINDS,
        weights=[0.45, 0.30, 0.25],
        k=1,
    )[0]

    base_hp = (22 + state.wave * 5) * diff
    base_spd = (55 + min(state.wave, 25) * 2) * (1.0 + (diff - 1.0) * 0.35)
    base_dmg = (6 + state.wave * 0.4) * diff
    base_xp = (6 + state.wave * 0.5) * (0.85 + diff * 0.08)

    hp, spd, dmg, xp, radius = stats_for_kind(kind, base_hp, base_spd, base_dmg, base_xp)
    hp *= scale

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
        )
    )
