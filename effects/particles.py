"""
Partículas genéricas (listas no GameState) — muzzle, impacto, morte, armas.
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
    elif kind == EnemyKind.FALLEN_ANGEL:
        palette = ((200, 190, 220), (120, 100, 160), (90, 70, 130))
    elif kind == EnemyKind.SKITTER:
        palette = ((120, 90, 140), (90, 70, 110), (160, 120, 180))
    elif kind == EnemyKind.BULWARK:
        palette = ((70, 65, 85), (100, 95, 115), (50, 48, 65))
    elif kind == EnemyKind.HERETIC:
        palette = ((160, 100, 90), (200, 140, 120), (120, 70, 60))
    elif kind == EnemyKind.CARRION_BOMB:
        palette = ((90, 140, 70), (140, 200, 80), (60, 90, 50))
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


def spawn_arc_slash(state: Any, x: float, y: float, angle: float, reach: float) -> None:
    for i in range(10):
        t = i / 9.0
        a = angle + (t - 0.5) * 1.1
        px = x + math.cos(a) * reach * (0.4 + 0.55 * t)
        py = y + math.sin(a) * reach * (0.4 + 0.55 * t)
        _add(
            state,
            px,
            py,
            math.cos(a) * random.uniform(40, 120),
            math.sin(a) * random.uniform(40, 120),
            random.uniform(0.1, 0.22),
            random.choice(((255, 220, 180), (255, 200, 140), (240, 180, 255))),
        )


def spawn_whip_line(state: Any, x: float, y: float, ux: float, uy: float, length: float) -> None:
    for i in range(12):
        t = i / 11.0
        px = x + ux * length * t + random.uniform(-4, 4)
        py = y + uy * length * t + random.uniform(-4, 4)
        _add(
            state,
            px,
            py,
            ux * random.uniform(20, 80) + random.uniform(-30, 30),
            uy * random.uniform(20, 80) + random.uniform(-30, 30),
            random.uniform(0.08, 0.2),
            random.choice(((200, 100, 200), (160, 80, 180), (255, 200, 255))),
        )


def spawn_fire_ring(state: Any, x: float, y: float, radius: float) -> None:
    n = max(16, int(radius / 10))
    for i in range(n):
        a = (math.tau / n) * i
        px = x + math.cos(a) * radius
        py = y + math.sin(a) * radius
        _add(
            state,
            px,
            py,
            math.cos(a) * random.uniform(30, 90),
            math.sin(a) * random.uniform(30, 90),
            random.uniform(0.12, 0.28),
            random.choice(((255, 140, 60), (255, 200, 80), (255, 90, 40))),
        )


def spawn_holy_splash(state: Any, x: float, y: float) -> None:
    for _ in range(14):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(40, 160)
        _add(
            state,
            x,
            y,
            math.cos(ang) * spd,
            math.sin(ang) * spd,
            random.uniform(0.2, 0.45),
            random.choice(((180, 220, 255), (140, 200, 255), (220, 255, 240))),
        )


def spawn_fire_burst(state: Any, x: float, y: float, radius: float) -> None:
    for _ in range(18):
        ang = random.uniform(0, math.tau)
        r = random.uniform(0.15, 1.0) * radius
        px = x + math.cos(ang) * r
        py = y + math.sin(ang) * r
        _add(
            state,
            px,
            py,
            math.cos(ang) * random.uniform(60, 180),
            math.sin(ang) * random.uniform(60, 180),
            random.uniform(0.18, 0.4),
            random.choice(((255, 160, 50), (255, 220, 100), (255, 80, 30))),
        )


def spawn_lightning_jolt(
    state: Any, x0: float, y0: float, x1: float, y1: float
) -> None:
    steps = 5
    for s in range(steps + 1):
        t = s / steps
        mx = (x0 * (1 - t) + x1 * t) + random.uniform(-10, 10)
        my = (y0 * (1 - t) + y1 * t) + random.uniform(-10, 10)
        _add(
            state,
            mx,
            my,
            random.uniform(-40, 40),
            random.uniform(-40, 40),
            random.uniform(0.08, 0.16),
            random.choice(((220, 240, 255), (180, 200, 255), (255, 255, 255))),
        )


def spawn_bible_collect(state: Any, x: float, y: float) -> None:
    for _ in range(28):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(60, 220)
        _add(
            state,
            x,
            y,
            math.cos(ang) * spd,
            math.sin(ang) * spd,
            random.uniform(0.35, 0.65),
            random.choice(((255, 230, 140), (240, 200, 100), (255, 255, 220), (200, 220, 255))),
        )


def spawn_possession_flash(state: Any, x: float, y: float) -> None:
    for _ in range(20):
        ang = random.uniform(0, math.tau)
        spd = random.uniform(30, 140)
        _add(
            state,
            x,
            y,
            math.cos(ang) * spd,
            math.sin(ang) * spd,
            random.uniform(0.25, 0.5),
            random.choice(((200, 255, 220), (255, 200, 255), (180, 255, 255))),
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
