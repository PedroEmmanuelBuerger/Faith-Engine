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

        # Progressão
        self.xp = 0.0
        self.level = 1
        self.level_up_paused = False
        self.xp_to_next = 30.0
        self._recalc_xp_to_next()

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

        for e in self.enemies:
            d = self._dist_player_enemy(e)
            if d <= e.radius + p.radius:
                eid = id(e)
                if eid not in self._enemy_hit_timer or self._enemy_hit_timer[eid] <= 0:
                    p.take_damage(e.damage)
                    self._enemy_hit_timer[eid] = self.contact_cooldown

    def update(self, dt: float) -> None:
        if self.player.hp <= 0 or self.level_up_paused:
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = self.spawn_interval

        target = (self.player.x, self.player.y)
        for e in self.enemies:
            e.update(dt, target)

        self._apply_contact_damage(dt)
        self._update_aura(dt)

    def _recalc_xp_to_next(self) -> None:
        """Curva de XP por nível (exponencial suave)."""
        self.xp_to_next = int(28 * (1.2 ** (self.level - 1)))

    def _grant_xp(self, amount: float) -> None:
        if self.level_up_paused or self.player.hp <= 0:
            return
        self.xp += amount
        self._try_level_up()

    def _try_level_up(self) -> None:
        """Sobe um nível por vez e pausa até o jogador resolver a escolha."""
        if self.xp < self.xp_to_next:
            return
        self.xp -= self.xp_to_next
        self.level += 1
        self._recalc_xp_to_next()
        self.level_up_paused = True

    def acknowledge_level_up_placeholder(self) -> None:
        """Commit 4: bônus simples até o sistema de cartas entrar."""
        if not self.level_up_paused:
            return
        self.level_up_paused = False
        self.player.max_hp += 5
        self.player.hp = min(self.player.hp + 15, self.player.max_hp)
        # Se ainda houver XP suficiente, enfileira outro nível.
        self._try_level_up()

    def _update_aura(self, dt: float) -> None:
        """Pulso de aura: dano em área a cada aura_interval."""
        p = self.player
        if p.hp <= 0 or self.level_up_paused:
            return
        p.aura_timer += dt
        if p.aura_timer < p.aura_interval:
            return
        p.aura_timer = 0.0
        dmg = p.effective_damage
        rng = p.effective_range
        alive: List[Enemy] = []
        for e in self.enemies:
            if self._dist_player_enemy(e) <= rng + e.radius:
                if e.take_damage(dmg):
                    self._grant_xp(e.xp_value)
                else:
                    alive.append(e)
            else:
                alive.append(e)
        self.enemies = alive

    def reset_run(self) -> None:
        """Reinicia posição e inimigos (útil depois para prestige/morte)."""
        self.enemies.clear()
        self._enemy_hit_timer.clear()
        self.player = Player(self.width / 2, self.height / 2)
        self.spawn_timer = 0.0
        self.wave = 1
        self.xp = 0.0
        self.level = 1
        self._recalc_xp_to_next()
        self.level_up_paused = False
