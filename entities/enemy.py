"""
Inimigos com variedade visual (sacerdote corrupto, estátua, sombra).
`kind` + `sprite_key` permitem trocar por sprites sem mudar a IA.
"""

from __future__ import annotations

import math
from typing import Tuple


class EnemyKind:
    CORRUPT_PRIEST = "priest"
    POSSESSED_STATUE = "statue"
    SHADOW_CREATURE = "shadow"


class Enemy:
    def __init__(
        self,
        x: float,
        y: float,
        max_hp: float,
        speed: float,
        damage: float,
        radius: float = 14.0,
        xp_value: float = 8.0,
        kind: str = EnemyKind.CORRUPT_PRIEST,
        sprite_key: str | None = None,
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.max_hp = float(max_hp)
        self.hp = self.max_hp
        self.speed = float(speed)
        self.damage = float(damage)
        self.radius = float(radius)
        self.xp_value = float(xp_value)
        self.kind = kind
        self.sprite_key = sprite_key or kind

        # Flash ao levar dano (feedback)
        self.hit_flash = 0.0

    def update(self, dt: float, target: Tuple[float, float]) -> None:
        tx, ty = target
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            return
        dx /= dist
        dy /= dist
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        self.hit_flash = max(0.0, self.hit_flash - dt * 5.0)

    def take_damage(self, amount: float) -> bool:
        self.hp -= amount
        self.hit_flash = 1.0
        return self.hp <= 0


def stats_for_kind(
    kind: str, base_hp: float, base_spd: float, base_dmg: float, base_xp: float
) -> tuple[float, float, float, float, float]:
    """Multiplicadores por tipo — fácil de balancear."""
    if kind == EnemyKind.POSSESSED_STATUE:
        return base_hp * 1.35, base_spd * 0.72, base_dmg * 1.15, base_xp * 1.1, 18.0
    if kind == EnemyKind.SHADOW_CREATURE:
        return base_hp * 0.75, base_spd * 1.25, base_dmg * 0.9, base_xp * 0.95, 12.0
    return base_hp, base_spd, base_dmg, base_xp, 14.0
