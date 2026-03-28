"""
Spawn em anel à volta do jogador (mapa infinito).
Fases de dificuldade, mini-chefes e variedade de tipos.
"""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, List, Tuple

from core import config
from entities.enemy import Enemy, EnemyKind, stats_for_kind

if TYPE_CHECKING:
    from core.game_state import GameState

_BASE_KINDS = (
    EnemyKind.CORRUPT_PRIEST,
    EnemyKind.SHADOW_CREATURE,
    EnemyKind.POSSESSED_STATUE,
    EnemyKind.FALLEN_ANGEL,
    EnemyKind.SKITTER,
    EnemyKind.BULWARK,
    EnemyKind.HERETIC,
    EnemyKind.CARRION_BOMB,
    EnemyKind.PENITENT_CHARGER,
    EnemyKind.SCHISM_SPLITTER,
)

# Pesos por fase: (early, mid, late) — normalizados depois
_PHASE_WEIGHT_ROWS: Tuple[Tuple[float, ...], ...] = (
    (0.16, 0.16, 0.12, 0.11, 0.14, 0.07, 0.11, 0.09, 0.02, 0.02),
    (0.14, 0.14, 0.11, 0.10, 0.13, 0.08, 0.11, 0.10, 0.05, 0.04),
    (0.11, 0.12, 0.09, 0.09, 0.12, 0.09, 0.10, 0.10, 0.10, 0.08),
)


def _phase_index(t: float) -> int:
    if t < 72.0:
        return 0
    if t < 200.0:
        return 1
    return 2


def _weights_for_state(state: GameState) -> List[float]:
    row = _PHASE_WEIGHT_ROWS[_phase_index(state.difficulty_time)]
    w = list(row)
    # Onda alta: mais caos (charger / splitter)
    if state.wave >= 6:
        w[8] += 0.04
        w[9] += 0.03
    if state.wave >= 12:
        w[5] += 0.02
        w[2] += 0.02
    s = sum(w) or 1.0
    return [x / s for x in w]


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


def _spawn_enemy_at(
    state: GameState,
    x: float,
    y: float,
    kind: str,
    *,
    is_miniboss: bool = False,
) -> None:
    if len(state.enemies) >= config.MAX_ENEMIES_ALIVE:
        return

    base_hp = 24.0
    base_spd = 68.0
    base_dmg = 7.0
    base_xp = 7.0

    phase = _phase_index(state.difficulty_time)
    spd_scale = (0.88, 1.0, 1.06)[phase]
    base_spd *= spd_scale

    hp, spd, dmg, xp, radius = stats_for_kind(kind, base_hp, base_spd, base_dmg, base_xp)

    if is_miniboss:
        hp *= 2.35
        spd *= 0.92
        dmg *= 1.08
        radius *= 1.38
        xp *= 1.25

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
            is_miniboss=is_miniboss,
        )
    )


def _spawn_one(state: GameState) -> None:
    x, y = _random_point_outside_view(state)
    weights = _weights_for_state(state)
    kind = random.choices(_BASE_KINDS, weights=weights, k=1)[0]
    _spawn_enemy_at(state, x, y, kind, is_miniboss=False)


def spawn_enemy(state: GameState) -> None:
    pressure = state.spawn_pressure
    count = 1
    extra = int((pressure - 1.0) * 0.95)
    count += min(4, max(0, extra))
    if state.wave >= 3 and random.random() < 0.26:
        count += 1
    if state.wave >= 8 and random.random() < 0.16:
        count += 1

    for _ in range(count):
        if len(state.enemies) >= config.MAX_ENEMIES_ALIVE:
            break
        _spawn_one(state)
    _trim_excess_enemies(state)


def try_spawn_miniboss(state: GameState) -> None:
    if len(state.enemies) >= config.MAX_ENEMIES_ALIVE - 1:
        return
    x, y = _random_point_outside_view(state)
    kind = random.choice(
        (
            EnemyKind.BULWARK,
            EnemyKind.POSSESSED_STATUE,
            EnemyKind.FALLEN_ANGEL,
            EnemyKind.SCHISM_SPLITTER,
        )
    )
    _spawn_enemy_at(state, x, y, kind, is_miniboss=True)
