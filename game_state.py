"""
Estado global da partida: lista de inimigos, ondas, XP e escolha de upgrades.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List

from enemy import Enemy, random_edge_position
from player import Player

import upgrades


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

        # Upgrades
        self.upgrade_counts: Dict[str, int] = {}
        self.upgrade_choice_ids: List[str] = []
        self.synergy_zeal_active = False

        # Fé (valor usado no commit seguinte; multiplicador já vem das cartas)
        self.faith = 0.0
        self.followers = 1.0
        self.faith_rate_multiplier = 1.0
        self.prestige_faith_mult = 1.0
        self.prestige_points = 0

        # Profeta Louco
        self.mad_prophet_stacks = 0
        self.mad_prophet_timer = 0.0
        self._prophet_dmg_left = 0.0
        self._prophet_rng_left = 0.0

        self.contact_cooldown = 0.6
        self._enemy_hit_timer: dict[int, float] = {}

        # Feedback visual
        self.particles: List[dict] = []
        self.screen_shake = 0.0
        self.damage_flash = 0.0

        # Dificuldade global ao longo do tempo
        self.difficulty_time = 0.0

        upgrades.refresh_stats(self)

    def passive_faith_per_second(self) -> float:
        """Seguidores geram fé passiva; multiplicadores vêm das cartas e do prestige."""
        base = 0.35 * self.followers
        return base * self.faith_rate_multiplier

    def add_click_faith(self) -> None:
        """Clique: injeção manual de fé (loop viciante)."""
        self.faith += 1.2 * self.faith_rate_multiplier

    def can_prestige(self) -> bool:
        """Requer fé acumulada e partida fora do menu de nível."""
        return self.faith >= 400.0 and not self.level_up_paused

    def do_prestige(self) -> bool:
        """
        Reinicia a corrida mantendo pontos de transcendência.
        Cada ponto concede +12% geração de fé permanente nesta sessão.
        """
        if not self.can_prestige():
            return False
        self.prestige_points += 1
        self.reset_run(keep_meta=True)
        return True

    @property
    def difficulty_mult(self) -> float:
        """Aumenta HP/dano dos inimigos com o tempo sobrevivido."""
        return 1.0 + self.difficulty_time * 0.018

    def spawn_enemy(self) -> None:
        scale = 1.0 + (self.wave - 1) * 0.08
        diff = self.difficulty_mult
        x, y = random_edge_position(self.width, self.height)
        hp = (22 + self.wave * 5) * diff
        spd = (55 + min(self.wave, 25) * 2) * (1.0 + (diff - 1.0) * 0.35)
        dmg = (6 + self.wave * 0.4) * diff
        self.enemies.append(
            Enemy(
                x,
                y,
                max_hp=hp * scale,
                speed=spd,
                damage=dmg,
                radius=14,
                xp_value=(6 + self.wave * 0.5) * (0.85 + diff * 0.08),
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
                    self.screen_shake = max(self.screen_shake, 8.0)
                    self.damage_flash = min(0.85, self.damage_flash + 0.35)

    def _tick_mad_prophet(self, dt: float) -> None:
        self._prophet_dmg_left = max(0.0, self._prophet_dmg_left - dt)
        self._prophet_rng_left = max(0.0, self._prophet_rng_left - dt)

        stacks = self.mad_prophet_stacks
        if stacks <= 0:
            self.mad_prophet_timer = 0.0
            return

        self.mad_prophet_timer += dt
        interval = 5.0 / (1.0 + 0.25 * max(0, stacks - 1))
        if self.mad_prophet_timer < interval:
            return
        self.mad_prophet_timer = 0.0

        roll = random.choice(("dmg", "range", "faith", "heal"))
        if roll == "dmg":
            self._prophet_dmg_left = 2.8
        elif roll == "range":
            self._prophet_rng_left = 2.8
        elif roll == "faith":
            self.faith += 12 + stacks * 4
        else:
            self.player.hp = min(self.player.max_hp, self.player.hp + 10 + stacks * 2)

    def update(self, dt: float) -> None:
        self.difficulty_time += dt

        if self.player.hp <= 0 or self.level_up_paused:
            return

        self.faith += self.passive_faith_per_second() * dt

        self._tick_mad_prophet(dt)

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            # Spawn mais rápido conforme a onda e o tempo (teto para não virar caos instantâneo)
            self.spawn_timer = max(
                0.35, self.spawn_interval / (1.0 + self.wave * 0.04 + self.difficulty_time * 0.02)
            )

        target = (self.player.x, self.player.y)
        for e in self.enemies:
            e.update(dt, target)

        self._apply_contact_damage(dt)
        self._update_aura(dt)

    def _recalc_xp_to_next(self) -> None:
        self.xp_to_next = int(28 * (1.2 ** (self.level - 1)))

    def _grant_xp(self, amount: float) -> None:
        if self.level_up_paused or self.player.hp <= 0:
            return
        self.xp += amount
        self._try_level_up()

    def _try_level_up(self) -> None:
        if self.xp < self.xp_to_next:
            return
        self.xp -= self.xp_to_next
        self.level += 1
        self._recalc_xp_to_next()
        self.level_up_paused = True
        self.upgrade_choice_ids = upgrades.random_choices(3)

    def select_upgrade(self, index: int) -> None:
        if not self.level_up_paused:
            return
        if index < 0 or index >= len(self.upgrade_choice_ids):
            return
        uid = self.upgrade_choice_ids[index]
        upgrades.apply_upgrade(self, uid)
        self.upgrade_choice_ids = []
        self.level_up_paused = False
        self._try_level_up()

    def _prophet_damage_mult(self) -> float:
        return 1.35 if self._prophet_dmg_left > 0 else 1.0

    def _prophet_range_mult(self) -> float:
        return 1.25 if self._prophet_rng_left > 0 else 1.0

    def _update_aura(self, dt: float) -> None:
        p = self.player
        if p.hp <= 0 or self.level_up_paused:
            return
        p.aura_timer += dt
        if p.aura_timer < p.aura_interval:
            return
        p.aura_timer = 0.0
        dmg = p.effective_damage * self._prophet_damage_mult()
        rng = p.effective_range * self._prophet_range_mult()
        alive: List[Enemy] = []
        for e in self.enemies:
            if self._dist_player_enemy(e) <= rng + e.radius:
                if e.take_damage(dmg):
                    self._grant_xp(e.xp_value)
                    self._spawn_death_particles(e.x, e.y)
                else:
                    alive.append(e)
            else:
                alive.append(e)
        self.enemies = alive

    def _spawn_death_particles(self, x: float, y: float, n: int = 10) -> None:
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(40, 160)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(ang) * spd,
                    "vy": math.sin(ang) * spd,
                    "life": random.uniform(0.25, 0.55),
                    "col": random.choice(
                        ((255, 200, 120), (255, 120, 160), (200, 160, 255))
                    ),
                }
            )

    def update_particles_only(self, dt: float) -> None:
        """Partículas e decaimento de FX (sempre roda, inclusive na pausa de nível)."""
        self.damage_flash = max(0.0, self.damage_flash - dt * 1.1)
        self.screen_shake = max(0.0, self.screen_shake - dt * 22)
        newp: List[dict] = []
        for pt in self.particles:
            pt["life"] -= dt
            if pt["life"] <= 0:
                continue
            pt["x"] += pt["vx"] * dt
            pt["y"] += pt["vy"] * dt
            pt["vy"] += 180 * dt
            newp.append(pt)
        self.particles = newp

    def reset_run(self, keep_meta: bool = False) -> None:
        self.enemies.clear()
        self._enemy_hit_timer.clear()
        self.player = Player(self.width / 2, self.height / 2)
        self.spawn_timer = 0.0
        self.wave = 1
        self.xp = 0.0
        self.level = 1
        self._recalc_xp_to_next()
        self.level_up_paused = False
        self.upgrade_choice_ids = []
        self.faith = 0.0
        self.mad_prophet_timer = 0.0
        self._prophet_dmg_left = 0.0
        self._prophet_rng_left = 0.0
        self.difficulty_time = 0.0
        self.particles.clear()
        self.screen_shake = 0.0
        self.damage_flash = 0.0
        # Nova corrida: sempre zera o baralho atual; meta só preserva transcendência.
        self.upgrade_counts = {}
        if not keep_meta:
            self.prestige_points = 0
            self.prestige_faith_mult = 1.0
        else:
            self.prestige_faith_mult = 1.0 + 0.12 * self.prestige_points
        upgrades.refresh_stats(self)
