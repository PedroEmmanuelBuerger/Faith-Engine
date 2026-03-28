"""
Partículas genéricas (listas no GameState) — muzzle, impacto, morte.
"""

from __future__ import annotations

import math
import random
from typing import Any

from entities.enemy import EnemyKind


def _add(state: Any, x: float, y: float, vx: float, vy: float, life: float, col: tuple) -> None:
    state.particles.append(
        {"x": x, "y": y, "vx": vx, "vy": vy, "life": life, "col": col}
    )


def spawn_muzzle(state: Any, x: float, y: float, ux: float, uy: float) -> None:
    for _ in range(6):
        ang = math.atan2(uy, ux) + random.uniform(-0.5, 0.5)
        spd = random.uniform(30, 120)
        _add(
            state,
            x,
            y,
            math.cos(ang) * spd,
            math.sin(ang) * spd,
            random.uniform(0.12, 0.28),
            random.choice(((255, 230, 200), (220, 180, 255), (255, 255, 255))),
        )


def spawn_hit_sparks(state: Any, x: float, y: float) -> None:
    for _ in range(8):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(80, 200)
        _add(
            state,
            x,
            y,
            math.cos(ang) * spd,
            math.sin(ang) * spd,
            random.uniform(0.15, 0.35),
            random.choice(((255, 220, 160), (255, 200, 120))),
        )


def spawn_death_burst(state: Any, x: float, y: float, kind: str) -> None:
    if kind == EnemyKind.POSSESSED_STATUE:
        palette = ((180, 175, 190), (140, 135, 155), (220, 210, 230))
    elif kind == EnemyKind.SHADOW_CREATURE:
        palette = ((80, 60, 120), (120, 80, 160), (40, 30, 70))
    else:
        palette = ((200, 100, 120), (160, 80, 100), (255, 180, 190))

    for _ in range(14):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(50, 200)
        _add(
            state,
            x,
            y,
            math.cos(ang) * spd,
            math.sin(ang) * spd,
            random.uniform(0.3, 0.65),
            random.choice(palette),
        )


def spawn_projectile_trail(state: Any, x: float, y: float) -> None:
    _add(
        state,
        x + random.uniform(-2, 2),
        y + random.uniform(-2, 2),
        random.uniform(-20, 20),
        random.uniform(-20, 20),
        random.uniform(0.08, 0.18),
        (200, 180, 255),
    )


def update_particles(state: Any, dt: float) -> None:
    state.damage_flash = max(0.0, state.damage_flash - dt * 1.15)
    state.screen_shake = max(0.0, state.screen_shake - dt * 24)
    newp = []
    for pt in state.particles:
        pt["life"] -= dt
        if pt["life"] <= 0:
            continue
        pt["x"] += pt["vx"] * dt
        pt["y"] += pt["vy"] * dt
        pt["vy"] += 140 * dt
        newp.append(pt)
    state.particles = newp
