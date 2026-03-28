"""
Jogador: movimento, stats e animação (sprites vêm da UI).
"""

from core import config


class Player:
    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.radius = 16

        self.facing_right: bool = True
        # Vista para sprites: lado, frente (sul) ou costas (norte) no movimento predominante
        self.view_facing: str = "south"
        self.is_walking: bool = False
        self.walk_frame: int = 0
        self._walk_anim_t: float = 0.0

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

    def move(
        self,
        dx: float,
        dy: float,
        dt: float,
        world_w: float | None = None,
        world_h: float | None = None,
    ) -> None:
        self.is_walking = dx != 0 or dy != 0
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        if self.is_walking:
            if abs(dy) >= abs(dx) and dy != 0:
                self.view_facing = "north" if dy < 0 else "south"
            elif dx != 0:
                self.view_facing = "side"

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
