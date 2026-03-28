"""
Projétil com variantes: raio, frasco sagrado, ricochetes, perfuração.
"""

from __future__ import annotations

import math


class Projectile:
    __slots__ = (
        "x",
        "y",
        "vx",
        "vy",
        "damage",
        "radius",
        "alive",
        "life",
        "kind",
        "bounces_remaining",
        "pierce_remaining",
        "spawns_pool",
    )

    def __init__(
        self,
        x: float,
        y: float,
        direction_x: float,
        direction_y: float,
        speed: float,
        damage: float,
        radius: float = 5.0,
        max_range: float = 900.0,
        kind: str = "bolt",
        bounces_remaining: int = 0,
        pierce_remaining: int = 0,
        spawns_pool: bool = False,
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        length = math.hypot(direction_x, direction_y) or 1.0
        self.vx = direction_x / length * speed
        self.vy = direction_y / length * speed
        self.damage = float(damage)
        self.radius = float(radius)
        self.alive = True
        self.life = float(max_range) / max(speed, 1.0)
        self.kind = kind
        self.bounces_remaining = int(bounces_remaining)
        self.pierce_remaining = int(pierce_remaining)
        self.spawns_pool = bool(spawns_pool)

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False
