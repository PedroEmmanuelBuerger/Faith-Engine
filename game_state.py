"""
Estado global da partida: lista de inimigos, spawn por ondas e contato com o jogador.
"""

from __future__ import annotations

import math
from typing import List

from enemy import Enemy, random_edge_position
from player import Player


class GameState:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.player = Player(width / 2, height / 2)
        self.enemies: List[Enemy] = []

        self.spawn_timer = 0.0
        self.spawn_interval = 2.2
        self.wave = 1

        # Contato: intervalo entre danos do mesmo inimigo
        self.contact_cooldown = 0.6
        self._enemy_hit_timer: dict[int, float] = {}

    def spawn_enemy(self) -> None:
        """Cria um inimigo na borda; stats escalam levemente com a onda."""
        scale = 1.0 + (self.wave - 1) * 0.08
        x, y = random_edge_position(self.width, self.height)
        hp = 22 + self.wave * 5
        spd = 55 + min(self.wave, 25) * 2
        dmg = 6 + self.wave * 0.4
        self.enemies.append(
            Enemy(
                x,
                y,
                max_hp=hp * scale,
                speed=spd,
                damage=dmg,
                radius=14,
                xp_value=6 + self.wave * 0.5,
            )
        )

    def _dist_player_enemy(self, e: Enemy) -> float:
        p = self.player
        return math.hypot(e.x - p.x, e.y - p.y)

    def _apply_contact_damage(self, dt: float) -> None:
        p = self.player
        to_remove_keys: List[int] = []
        for eid, t in self._enemy_hit_timer.items():
            self._enemy_hit_timer[eid] = t - dt
            if self._enemy_hit_timer[eid] <= 0:
                to_remove_keys.append(eid)
        for k in to_remove_keys:
            del self._enemy_hit_timer[k]

        for i, e in enumerate(self.enemies):
            d = self._dist_player_enemy(e)
            if d <= e.radius + p.radius:
                eid = id(e)
                if eid not in self._enemy_hit_timer or self._enemy_hit_timer[eid] <= 0:
                    p.take_damage(e.damage)
                    self._enemy_hit_timer[eid] = self.contact_cooldown

    def update(self, dt: float) -> None:
        if self.player.hp <= 0:
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = self.spawn_interval

        target = (self.player.x, self.player.y)
        for e in self.enemies:
            e.update(dt, target)

        self._apply_contact_damage(dt)

    def reset_run(self) -> None:
        """Reinicia posição e inimigos (útil depois para prestige/morte)."""
        self.enemies.clear()
        self._enemy_hit_timer.clear()
        self.player = Player(self.width / 2, self.height / 2)
        self.spawn_timer = 0.0
        self.wave = 1
