"""
Inimigos: movem-se em linha reta até o jogador e causam dano ao encostar.
"""

from __future__ import annotations

import math
import random
from typing import Tuple


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
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.max_hp = float(max_hp)
        self.hp = self.max_hp
        self.speed = float(speed)
        self.damage = float(damage)
        self.radius = float(radius)
        self.xp_value = float(xp_value)

    def update(self, dt: float, target: Tuple[float, float]) -> None:
        """IA simples: direção ao alvo, velocidade constante."""
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

    def take_damage(self, amount: float) -> bool:
        self.hp -= amount
        return self.hp <= 0


def random_edge_position(width: int, height: int, margin: float = 40.0) -> Tuple[float, float]:
    """Ponto aleatório nas bordas da tela (para spawn)."""
    edge = random.randint(0, 3)
    if edge == 0:
        return random.uniform(margin, width - margin), margin
    if edge == 1:
        return random.uniform(margin, width - margin), height - margin
    if edge == 2:
        return margin, random.uniform(margin, height - margin)
    return width - margin, random.uniform(margin, height - margin)
