"""
Estado central da partida: mundo, câmara, entidades e flags de UI.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List

from core import config as game_config
from core import sfx, utils
from entities.enemy import Enemy
from entities.player import Player
from entities.projectile import Projectile
from effects import particles as particle_fx
from systems import combat_system, progression_system, spawn_system, upgrade_system
from world.chunk_world import ChunkWorld


class GameState:
    def __init__(self, world_seed: int | None = None) -> None:
        seed = world_seed if world_seed is not None else random.randint(1, 2**31 - 1)
        self.world_seed = seed
        self.world = ChunkWorld(seed)

        self.player = Player(0.0, 0.0)
        self.aim_world_x = self.player.x + 140.0
        self.aim_world_y = self.player.y
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []

        self.camera_x = 0.0
        self.camera_y = 0.0

        self.spawn_timer = 0.0
        self.spawn_interval = game_config.SPAWN_INTERVAL_BASE
        self.wave = 1
        self.total_kills = 0

        self.xp = 0.0
        self.level = 1
        self.level_up_paused = False
        self.xp_to_next = 30.0
        progression_system.recalc_xp_to_next(self)

        self.upgrade_counts: Dict[str, int] = {}
        self.upgrade_choice_ids: List[str] = []
        self.synergy_zeal_active = False

        self.faith = 0.0
        self.followers = 1.0
        self.faith_rate_multiplier = 1.0
        self.prestige_faith_mult = 1.0
        self.prestige_points = 0

        self.mad_prophet_stacks = 0
        self.mad_prophet_timer = 0.0
        self._prophet_dmg_left = 0.0
        self._prophet_spd_left = 0.0

        self.contact_cooldown = 0.6
        self._enemy_hit_timer: dict[int, float] = {}

        self.particles: List[dict] = []
        self.screen_shake = 0.0
        self.damage_flash = 0.0

        self.difficulty_time = 0.0

        self.melee_swings: List[dict] = []
        self.whip_strikes: List[dict] = []
        self.ground_pools: List[dict] = []
        self.pending_radial_pulses: List[dict] = []
        self.orbital_phase = 0.0
        self.orbital_debug: List[tuple[float, float]] = []
        self.enemy_bullets: List[dict[str, Any]] = []

        self.active_weapon_id = "w_dark_bolt"
        self.weapon_loadout: List[str] = ["w_dark_bolt"]
        self.weapon_cooldowns: Dict[str, float] = {}
        self._weapon_base_interval = 0.95
        self.auto_attack_enabled = False
        self.weapon_orbit_phase = 0.0
        self.pickups: List[Dict[str, Any]] = []
        self.bible_spawn_timer = 28.0
        self.weapon_damage_mult = 1.0

        self.synergy_inferno = False
        self.synergy_explosion_radius_mult = 1.0
        self.synergy_toxic_baptism = False
        self.synergy_pool_dps_mult = 1.0
        self.synergy_pool_duration_bonus = 1.0
        self.synergy_orb_velocity = 1.0
        self.synergy_chain_echo = False
        self.chain_bonus_jumps = 0

        self.death_mode = "alive"
        self.death_fade = 0.0
        self.game_paused = False

        upgrade_system.refresh_stats(self)
        self._update_camera()

    def sync_aim_from_screen(self, mouse_x: int, mouse_y: int) -> None:
        self.aim_world_x, self.aim_world_y = utils.screen_to_world(
            float(mouse_x), float(mouse_y), self.camera_x, self.camera_y
        )

    def sync_player_facing(self) -> None:
        self.player.update_facing_toward(self.aim_world_x, self.aim_world_y)

    @property
    def spawn_pressure(self) -> float:
        return 1.0 + (self.wave - 1) * 0.042 + self.difficulty_time * 0.009

    def passive_faith_per_second(self) -> float:
        base = 0.35 * self.followers
        return base * self.faith_rate_multiplier

    def add_click_faith(self) -> None:
        self.faith += 1.2 * self.faith_rate_multiplier

    def can_prestige(self) -> bool:
        return (
            self.faith >= 400.0
            and not self.level_up_paused
            and self.death_mode == "alive"
        )

    def do_prestige(self) -> bool:
        if not self.can_prestige():
            return False
        self.prestige_points += 1
        self.reset_run(keep_meta=True)
        return True

    def prophet_projectile_damage_mult(self) -> float:
        return 1.35 if self._prophet_dmg_left > 0 else 1.0

    def prophet_projectile_speed_mult(self) -> float:
        return 1.28 if self._prophet_spd_left > 0 else 1.0

    def _update_camera(self) -> None:
        from core import config

        p = self.player
        self.camera_x = p.x - config.VIEWPORT_W / 2
        self.camera_y = p.y - config.VIEWPORT_H / 2

    def update(self, dt: float) -> None:
        if self.game_paused:
            return
        self.difficulty_time += dt
        particle_fx.update_particles(self, dt)

        if self.death_mode == "fading":
            self.death_fade += dt / 1.35
            self.screen_shake = max(self.screen_shake, 3.0)
            if self.death_fade >= 1.0:
                self.death_fade = 1.0
                self.death_mode = "await_click"
            return

        if self.death_mode == "await_click":
            return

        if self.level_up_paused:
            return

        self.weapon_orbit_phase += dt * 0.55
        from systems import pickup_system

        pickup_system.update(self, dt)

        self.player.tick_weapon_kick(dt)

        self.faith += self.passive_faith_per_second() * dt
        progression_system.tick_mad_prophet(self, dt)

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            spawn_system.spawn_enemy(self)
            self.spawn_timer = max(
                0.28,
                self.spawn_interval / self.spawn_pressure,
            )

        for e in self.enemies:
            e.update(dt, self)

        combat_system.update_contact_damage(self, dt)
        combat_system.update_projectiles(self, dt)

        self._update_camera()
        self.world.prune_caches(self.player.x, self.player.y)

        if self.player.hp <= 0 and self.death_mode == "alive":
            self.death_mode = "fading"
            self.death_fade = 0.0
            self.screen_shake = max(self.screen_shake, 14.0)
            sfx.play_death()

    def move_player(self, dx: float, dy: float, dt: float) -> None:
        if (
            self.game_paused
            or self.level_up_paused
            or self.death_mode != "alive"
            or self.player.hp <= 0
        ):
            return
        from systems import world_collision

        self.player.move(dx, dy, dt, None, None)
        world_collision.resolve_player_vs_solids(self.player, self.world)
        self._update_camera()

    def select_upgrade(self, index: int) -> None:
        progression_system.select_upgrade(self, index)

    def reset_run(self, keep_meta: bool = False) -> None:
        self.enemies.clear()
        self.projectiles.clear()
        self.enemy_bullets.clear()
        self.melee_swings.clear()
        self.whip_strikes.clear()
        self.ground_pools.clear()
        self.pending_radial_pulses.clear()
        self.orbital_phase = 0.0
        self.orbital_debug.clear()
        self._enemy_hit_timer.clear()
        self.world.clear_caches()
        self.world_seed = random.randint(1, 2**31 - 1)
        self.world = ChunkWorld(self.world_seed)

        self.player = Player(0.0, 0.0)
        self.aim_world_x = self.player.x + 140.0
        self.aim_world_y = self.player.y
        self.spawn_timer = 0.0
        self.spawn_interval = game_config.SPAWN_INTERVAL_BASE
        self.wave = 1
        self.total_kills = 0
        self.xp = 0.0
        self.level = 1
        progression_system.recalc_xp_to_next(self)
        self.level_up_paused = False
        self.upgrade_choice_ids = []
        self.faith = 0.0
        self.mad_prophet_timer = 0.0
        self._prophet_dmg_left = 0.0
        self._prophet_spd_left = 0.0
        self.difficulty_time = 0.0
        self.particles.clear()
        self.screen_shake = 0.0
        self.damage_flash = 0.0
        self.death_mode = "alive"
        self.death_fade = 0.0
        self.game_paused = False
        self.upgrade_counts = {}
        self.weapon_loadout = ["w_dark_bolt"]
        self.weapon_cooldowns.clear()
        self._weapon_base_interval = 0.95
        self.auto_attack_enabled = False
        self.weapon_orbit_phase = 0.0
        self.pickups.clear()
        self.bible_spawn_timer = 28.0
        self.active_weapon_id = "w_dark_bolt"
        if not keep_meta:
            self.prestige_points = 0
            self.prestige_faith_mult = 1.0
        else:
            self.prestige_faith_mult = 1.0 + 0.12 * self.prestige_points
        upgrade_system.refresh_stats(self)
        self._update_camera()
