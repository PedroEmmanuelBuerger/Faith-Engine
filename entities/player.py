"""
Jogador: movimento, stats, facing (rato/movimento) e arma equipada.
"""

from __future__ import annotations

import math
from enum import Enum, auto
from typing import TYPE_CHECKING

from core import config

if TYPE_CHECKING:
    from entities.weapon import Weapon


class FaceDirection(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


class Player:
    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.radius = 16

        self.facing_right: bool = True
        self.facing_dir: FaceDirection = FaceDirection.DOWN
        self.equipped_weapon: Weapon | None = None
        self.weapon_visual_kick: float = 0.0

        self.is_walking: bool = False
        self.walk_frame: int = 0
        self._walk_anim_t: float = 0.0
        self._last_input_dx: float = 0.0
        self._last_input_dy: float = 0.0

        self.max_hp = 100.0
        self.hp = self.max_hp

        self.base_damage = 11.0
        self.damage_multiplier = 1.0

        self.projectile_speed_mult = 1.0
        self.move_speed = 240.0

        self.shoot_interval = 1.0
        self.shoot_cooldown = 0.0

    @property
    def effective_damage(self) -> float:
        return self.base_damage * self.damage_multiplier

    @property
    def projectile_speed(self) -> float:
        return 420.0 * self.projectile_speed_mult

    def update_facing_toward(self, aim_world_x: float, aim_world_y: float) -> None:
        """Prioridade: vetor jogador → mira; senão último input de movimento."""
        dx = aim_world_x - self.x
        dy = aim_world_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 14.0:
            if abs(dx) >= abs(dy):
                self.facing_dir = FaceDirection.RIGHT if dx > 0 else FaceDirection.LEFT
                self.facing_right = dx > 0
            else:
                self.facing_dir = FaceDirection.DOWN if dy > 0 else FaceDirection.UP
            return
        lx, ly = self._last_input_dx, self._last_input_dy
        if self.is_walking and (lx != 0 or ly != 0):
            if abs(lx) >= abs(ly):
                self.facing_dir = FaceDirection.RIGHT if lx > 0 else FaceDirection.LEFT
                self.facing_right = lx > 0
            else:
                self.facing_dir = FaceDirection.DOWN if ly > 0 else FaceDirection.UP

    def tick_weapon_kick(self, dt: float) -> None:
        self.weapon_visual_kick = max(0.0, self.weapon_visual_kick - dt * 2.8)

    def move(
        self,
        dx: float,
        dy: float,
        dt: float,
        world_w: float | None = None,
        world_h: float | None = None,
    ) -> None:
        self._last_input_dx, self._last_input_dy = dx, dy
        self.is_walking = dx != 0 or dy != 0
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        if dx != 0 or dy != 0:
            length = (dx * dx + dy * dy) ** 0.5
            dx /= length
            dy /= length
        self.x += dx * self.move_speed * dt
        self.y += dy * self.move_speed * dt
        if world_w is not None:
            self.x = max(self.radius, min(world_w - self.radius, self.x))
        if world_h is not None:
            self.y = max(self.radius, min(world_h - self.radius, self.y))

        if self.is_walking:
            self._walk_anim_t += dt
            dur = config.PLAYER_WALK_FRAME_SEC
            while self._walk_anim_t >= dur:
                self._walk_anim_t -= dur
                self.walk_frame ^= 1
        else:
            self._walk_anim_t = 0.0
            self.walk_frame = 0

    def take_damage(self, amount: float) -> None:
        self.hp = max(0.0, self.hp - amount)
