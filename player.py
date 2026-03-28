"""
Jogador: posição, vida, dano e alcance da aura/ataque.
Movimento com WASD ou setas.
"""


class Player:
    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.radius = 18

        self.max_hp = 100.0
        self.hp = self.max_hp

        # Dano base da aura (multiplicadores vêm de upgrades no game_state)
        self.base_damage = 12.0
        self.damage_multiplier = 1.0

        # Alcance do pulso de aura em pixels
        self.attack_range = 110.0
        self.attack_range_multiplier = 1.0

        self.move_speed = 220.0

        # Cooldown da aura em segundos (reduzível por upgrades)
        self.aura_interval = 1.0
        self.aura_timer = 0.0

    @property
    def effective_damage(self) -> float:
        return self.base_damage * self.damage_multiplier

    @property
    def effective_range(self) -> float:
        return self.attack_range * self.attack_range_multiplier

    def move(self, dx: float, dy: float, dt: float, width: int, height: int) -> None:
        """Move o jogador e mantém dentro da arena."""
        if dx != 0 or dy != 0:
            length = (dx * dx + dy * dy) ** 0.5
            dx /= length
            dy /= length
        self.x += dx * self.move_speed * dt
        self.y += dy * self.move_speed * dt
        self.x = max(self.radius, min(width - self.radius, self.x))
        self.y = max(self.radius, min(height - self.radius, self.y))

    def take_damage(self, amount: float) -> None:
        self.hp = max(0.0, self.hp - amount)

    def heal_full(self) -> None:
        self.hp = self.max_hp
