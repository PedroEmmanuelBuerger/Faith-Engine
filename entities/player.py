"""
Jogador: cultista (desenho procedural — trocável por sprite depois).
Movimento no mundo; projéteis em vez de aura.
"""


class Player:
    """Cultista com manto escuro; olhos luminosos desenhados na camada de entidades."""

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.radius = 16

        self.max_hp = 100.0
        self.hp = self.max_hp

        self.base_damage = 11.0
        self.damage_multiplier = 1.0

        # Velocidade dos projéteis (antes era “alcance” da aura)
        self.projectile_speed_mult = 1.0
        self.move_speed = 240.0

        self.shoot_interval = 0.38
        self.shoot_cooldown = 0.0

    @property
    def effective_damage(self) -> float:
        return self.base_damage * self.damage_multiplier

    @property
    def projectile_speed(self) -> float:
        return 420.0 * self.projectile_speed_mult

    def move(self, dx: float, dy: float, dt: float, world_w: float, world_h: float) -> None:
        if dx != 0 or dy != 0:
            length = (dx * dx + dy * dy) ** 0.5
            dx /= length
            dy /= length
        self.x += dx * self.move_speed * dt
        self.y += dy * self.move_speed * dt
        self.x = max(self.radius, min(world_w - self.radius, self.x))
        self.y = max(self.radius, min(world_h - self.radius, self.y))

    def take_damage(self, amount: float) -> None:
        self.hp = max(0.0, self.hp - amount)
