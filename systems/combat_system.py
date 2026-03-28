"""
Projéteis, colisões e dano de contacto jogador–inimigo.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List

from core import config
from entities.projectile import Projectile
from effects import particles as particle_fx

if TYPE_CHECKING:
    from core.game_state import GameState
    from entities.enemy import Enemy


def try_shoot(state: GameState, target_world_x: float, target_world_y: float) -> None:
    """Dispara um projétil na direção do ponto no mundo (tipicamente o rato)."""
    p = state.player
    if p.shoot_cooldown > 0 or p.hp <= 0:
        return
    dx = target_world_x - p.x
    dy = target_world_y - p.y
    if dx == 0 and dy == 0:
        dx, dy = 1.0, 0.0

    dmg = p.effective_damage * state.prophet_projectile_damage_mult()
    spd = p.projectile_speed * state.prophet_projectile_speed_mult()

    # Saída ligeiramente à frente do corpo do cultista
    dist = math.hypot(dx, dy)
    ux, uy = dx / dist, dy / dist
    spawn_x = p.x + ux * (p.radius + 4)
    spawn_y = p.y + uy * (p.radius + 4)

    state.projectiles.append(
        Projectile(spawn_x, spawn_y, dx, dy, spd, dmg, radius=5.5, max_range=880.0)
    )
    p.shoot_cooldown = p.shoot_interval

    particle_fx.spawn_muzzle(state, spawn_x, spawn_y, ux, uy)


def _projectile_hits_enemy(px: float, py: float, pr: float, e: Enemy) -> bool:
    return math.hypot(px - e.x, py - e.y) <= pr + e.radius


def update_contact_damage(state: GameState, dt: float) -> None:
    p = state.player
    to_remove: List[int] = []
    for eid, t in state._enemy_hit_timer.items():
        state._enemy_hit_timer[eid] = t - dt
        if state._enemy_hit_timer[eid] <= 0:
            to_remove.append(eid)
    for k in to_remove:
        del state._enemy_hit_timer[k]

    for e in state.enemies:
        d = math.hypot(e.x - p.x, e.y - p.y)
        if d <= e.radius + p.radius:
            eid = id(e)
            if eid not in state._enemy_hit_timer or state._enemy_hit_timer[eid] <= 0:
                p.take_damage(e.damage)
                state._enemy_hit_timer[eid] = state.contact_cooldown
                state.screen_shake = max(state.screen_shake, 10.0)
                state.damage_flash = min(0.9, state.damage_flash + 0.4)


def update_projectiles(state: GameState, dt: float) -> None:
    p = state.player
    p.shoot_cooldown = max(0.0, p.shoot_cooldown - dt)

    alive_proj: List[Projectile] = []
    for proj in state.projectiles:
        proj.update(dt)
        if not proj.alive:
            continue
        # Limites do mundo
        if (
            proj.x < -40
            or proj.y < -40
            or proj.x > config.WORLD_W + 40
            or proj.y > config.WORLD_H + 40
        ):
            continue

        hit = False
        new_enemies = []
        for e in state.enemies:
            if hit:
                new_enemies.append(e)
                continue
            if _projectile_hits_enemy(proj.x, proj.y, proj.radius, e):
                dead = e.take_damage(proj.damage)
                if dead:
                    state.on_enemy_killed(e)
                    particle_fx.spawn_death_burst(state, e.x, e.y, e.kind)
                else:
                    particle_fx.spawn_hit_sparks(state, proj.x, proj.y)
                    new_enemies.append(e)
                hit = True
            else:
                new_enemies.append(e)
        state.enemies = new_enemies
        if not hit:
            alive_proj.append(proj)

    state.projectiles = alive_proj
