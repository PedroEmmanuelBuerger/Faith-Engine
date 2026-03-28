"""
Inimigos com variedade de papel (corpo-a-corpo, tanque, à distância, bomba).
`kind` + `sprite_key` permitem trocar por sprites sem mudar a IA.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from core.game_state import GameState


class EnemyKind:
    CORRUPT_PRIEST = "priest"
    FALLEN_ANGEL = "fallen_angel"
    POSSESSED_STATUE = "statue"
    SHADOW_CREATURE = "shadow"
    SKITTER = "skitter"
    BULWARK = "bulwark"
    HERETIC = "heretic"
    CARRION_BOMB = "carrion_bomb"
    PENITENT_CHARGER = "charger"
    SCHISM_SPLITTER = "splitter"


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
        *,
        explodes: bool = False,
        is_ranged: bool = False,
        is_miniboss: bool = False,
        split_depth: int = 0,
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

        self.explodes = explodes
        self.is_ranged = is_ranged
        self.is_miniboss = is_miniboss
        self.split_depth = split_depth
        self.shoot_cd = 0.0
        self.charmed_until = 0.0

        self.hit_flash = 0.0
        self.kb_vx = 0.0
        self.kb_vy = 0.0
        self._charger_cd = 0.8
        self._dash_t = 0.0

    def update(self, dt: float, state: GameState) -> None:
        self.hit_flash = max(0.0, self.hit_flash - dt * 6.5)
        if self.hp <= 0:
            return

        k_decay = math.exp(-11.0 * dt)
        self.kb_vx *= k_decay
        self.kb_vy *= k_decay
        self.x += self.kb_vx * dt
        self.y += self.kb_vy * dt

        tx, ty = state.player.x, state.player.y
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy) or 1.0
        ux, uy = dx / dist, dy / dist

        if self.charmed_until > 0:
            self.charmed_until -= dt
            best_o = None
            best_d = 1e9
            for o in state.enemies:
                if o is self or o.hp <= 0:
                    continue
                d = math.hypot(o.x - self.x, o.y - self.y)
                if d < best_d:
                    best_d = d
                    best_o = o
            if best_o is not None and best_d > 8:
                odx, ody = best_o.x - self.x, best_o.y - self.y
                od = math.hypot(odx, ody) or 1.0
                self.x += (odx / od) * self.speed * dt
                self.y += (ody / od) * self.speed * dt
            return

        if self.kind == EnemyKind.PENITENT_CHARGER:
            spd = self.speed * (2.35 if self._dash_t > 0 else 1.0)
            self._charger_cd -= dt
            if self._dash_t > 0:
                self._dash_t -= dt
                self.x += ux * spd * dt
                self.y += uy * spd * dt
            else:
                self.x += ux * self.speed * dt
                self.y += uy * self.speed * dt
                if self._charger_cd <= 0.0 and dist > 55:
                    self._dash_t = 0.38
                    self._charger_cd = 2.1 + random.uniform(0, 1.4)
            return

        if self.is_ranged:
            self.shoot_cd -= dt
            if 120 < dist < 400 and self.shoot_cd <= 0:
                spd = 220.0
                state.enemy_bullets.append(
                    {
                        "x": self.x + ux * (self.radius + 4),
                        "y": self.y + uy * (self.radius + 4),
                        "vx": ux * spd,
                        "vy": uy * spd,
                        "life": 2.4,
                        "dmg": self.damage * 0.85,
                    }
                )
                self.shoot_cd = 1.35
            if dist < 95:
                self.x -= ux * self.speed * 0.9 * dt
                self.y -= uy * self.speed * 0.9 * dt
            elif dist > 360:
                self.x += ux * self.speed * dt
                self.y += uy * self.speed * dt
            return

        self.x += ux * self.speed * dt
        self.y += uy * self.speed * dt

    def take_damage(self, amount: float) -> bool:
        self.hp -= amount
        self.hit_flash = 1.0
        return self.hp <= 0


def stats_for_kind(
    kind: str, base_hp: float, base_spd: float, base_dmg: float, base_xp: float
) -> tuple[float, float, float, float, float]:
    """Multiplicadores por tipo — HP/dano base fixos por onda (sem scaling temporal)."""
    if kind == EnemyKind.POSSESSED_STATUE:
        return base_hp * 1.35, base_spd * 0.72, base_dmg * 1.15, base_xp * 1.1, 18.0
    if kind == EnemyKind.FALLEN_ANGEL:
        return base_hp * 0.92, base_spd * 1.08, base_dmg * 1.05, base_xp * 1.08, 14.0
    if kind == EnemyKind.SHADOW_CREATURE:
        return base_hp * 0.75, base_spd * 1.25, base_dmg * 0.9, base_xp * 0.95, 12.0
    if kind == EnemyKind.SKITTER:
        return base_hp * 0.55, base_spd * 1.45, base_dmg * 0.75, base_xp * 0.85, 11.0
    if kind == EnemyKind.BULWARK:
        return base_hp * 1.9, base_spd * 0.52, base_dmg * 1.05, base_xp * 1.25, 22.0
    if kind == EnemyKind.HERETIC:
        return base_hp * 0.82, base_spd * 0.88, base_dmg * 0.95, base_xp * 1.05, 13.0
    if kind == EnemyKind.CARRION_BOMB:
        return base_hp * 0.68, base_spd * 1.05, base_dmg * 0.85, base_xp * 0.9, 15.0
    if kind == EnemyKind.PENITENT_CHARGER:
        return base_hp * 0.62, base_spd * 1.42, base_dmg * 0.82, base_xp * 1.05, 12.0
    if kind == EnemyKind.SCHISM_SPLITTER:
        return base_hp * 1.05, base_spd * 0.82, base_dmg * 0.95, base_xp * 1.15, 17.0
    return base_hp, base_spd, base_dmg, base_xp, 14.0
