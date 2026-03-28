"""
Combate: dano de armas, projéteis, contacto, habilidades (raio, possessão, rituais).
"""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, List

from core import config
from entities.enemy import Enemy
from entities.projectile import Projectile
from core import sfx
from effects import particles as particle_fx

if TYPE_CHECKING:
    from core.game_state import GameState


def _projectile_hits_enemy(px: float, py: float, pr: float, e: Enemy) -> bool:
    if e.hp <= 0:
        return False
    return math.hypot(px - e.x, py - e.y) <= pr + e.radius


def apply_weapon_hit(
    state: GameState, enemy: Enemy, damage: float, source: str
) -> None:
    """Ponto único de dano de armas — dispara possessão, morte e efeitos."""
    if enemy.hp <= 0:
        return
    dead = enemy.take_damage(damage)
    sfx.play_hit()
    particle_fx.spawn_hit_sparks(state, enemy.x, enemy.y)
    if dead:
        on_enemy_defeated(state, enemy, source)
    else:
        try_possession_on_hit(state, enemy)


def on_enemy_defeated(state: GameState, enemy: Enemy, source: str) -> None:
    if getattr(enemy, "explodes", False):
        _exploding_enemy_death(state, enemy)

    from systems import progression_system

    progression_system.grant_xp(state, enemy.xp_value)
    state.total_kills += 1
    if state.total_kills % 18 == 0:
        state.wave = min(99, state.wave + 1)

    particle_fx.spawn_death_burst(state, enemy.x, enemy.y, enemy.kind)

    stacks = state.upgrade_counts.get("flame_ritual", 0)
    if stacks > 0:
        rad = (55 + stacks * 12) * state.synergy_explosion_radius_mult
        dmg = state.player.effective_damage * 0.45 * stacks
        particle_fx.spawn_fire_burst(state, enemy.x, enemy.y, rad)
        for e in list(state.enemies):
            if e is enemy or e.hp <= 0:
                continue
            if math.hypot(e.x - enemy.x, e.y - enemy.y) <= rad + e.radius:
                apply_weapon_hit(state, e, dmg, "flame_ritual")


def _exploding_enemy_death(state: GameState, enemy: Enemy) -> None:
    rad, dmg = 95.0, 38.0
    p = state.player
    particle_fx.spawn_fire_ring(state, enemy.x, enemy.y, rad)
    for e in list(state.enemies):
        if e is enemy or e.hp <= 0:
            continue
        if math.hypot(e.x - enemy.x, e.y - enemy.y) <= rad + e.radius:
            apply_weapon_hit(state, e, dmg, "carrion_bomb")
    if math.hypot(p.x - enemy.x, p.y - enemy.y) <= rad + p.radius:
        p.take_damage(12.0)
        state.screen_shake = max(state.screen_shake, 9.0)


def try_possession_on_hit(state: GameState, enemy: Enemy) -> None:
    stacks = state.upgrade_counts.get("possession_hex", 0)
    if stacks <= 0:
        return
    if random.random() < 0.028 * stacks:
        enemy.charmed_until = 4.2
        particle_fx.spawn_possession_flash(state, enemy.x, enemy.y)


def chain_lightning_from(
    state: GameState,
    origin: Enemy,
    damage: float,
    jumps: int,
    already: set[int],
) -> None:
    if jumps <= 0:
        return
    best: tuple[float, Enemy] | None = None
    for e in state.enemies:
        if e is origin or id(e) in already or e.hp <= 0 or e.charmed_until > 0:
            continue
        d = math.hypot(e.x - origin.x, e.y - origin.y)
        if d < 155 and (best is None or d < best[0]):
            best = (d, e)
    if best is None:
        return
    _, tgt = best
    already.add(id(tgt))
    particle_fx.spawn_lightning_jolt(state, origin.x, origin.y, tgt.x, tgt.y)
    apply_weapon_hit(state, tgt, damage * 0.62, "chain")
    if jumps > 1 and tgt.hp > 0:
        chain_lightning_from(state, tgt, damage * 0.62, jumps - 1, already)


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
        if e.hp <= 0 or e.charmed_until > 0:
            continue
        d = math.hypot(e.x - p.x, e.y - p.y)
        if d <= e.radius + p.radius:
            eid = id(e)
            if eid not in state._enemy_hit_timer or state._enemy_hit_timer[eid] <= 0:
                p.take_damage(e.damage)
                state._enemy_hit_timer[eid] = state.contact_cooldown
                state.screen_shake = max(state.screen_shake, 10.0)
                state.damage_flash = min(0.9, state.damage_flash + 0.4)


def _resolve_projectile_hit(
    state: GameState, proj: Projectile, enemy: Enemy
) -> bool:
    """Devolve True se o projétil deve ser consumido."""
    already = {id(enemy)}
    apply_weapon_hit(state, enemy, proj.damage, proj.kind)
    if enemy.hp > 0 and proj.bounces_remaining > 0:
        chain_lightning_from(
            state, enemy, proj.damage, proj.bounces_remaining, already
        )

    if proj.pierce_remaining > 0:
        proj.pierce_remaining -= 1
        return False
    if proj.spawns_pool:
        from systems import weapon_system

        weapon_system.spawn_holy_pool(state, proj.x, proj.y)
    return True


def update_projectiles(state: GameState, dt: float) -> None:
    from systems import weapon_system

    p = state.player

    weapon_system.tick_weapon_cooldowns(state, dt)
    weapon_system.try_fire_all_weapons(state)
    weapon_system.update_melee_swings(state, dt)
    weapon_system.update_whip_strikes(state, dt)
    weapon_system.update_radial_pulse_visual(state, dt)
    weapon_system.update_ground_pools(state, dt)
    weapon_system.update_celestial_orbs(state, dt)

    alive_proj: List[Projectile] = []
    for proj in state.projectiles:
        proj.update(dt)
        if not proj.alive:
            if proj.kind == "holy_flask" and proj.spawns_pool:
                weapon_system.spawn_holy_pool(state, proj.x, proj.y)
            continue
        dist = math.hypot(proj.x - p.x, proj.y - p.y)
        if dist > config.PROJECTILE_MAX_DIST_FROM_PLAYER:
            if proj.kind == "holy_flask" and proj.spawns_pool:
                weapon_system.spawn_holy_pool(state, proj.x, proj.y)
            continue

        hit = False
        new_enemies = []
        for e in state.enemies:
            if hit:
                new_enemies.append(e)
                continue
            if _projectile_hits_enemy(proj.x, proj.y, proj.radius, e):
                consume = _resolve_projectile_hit(state, proj, e)
                if e.hp > 0:
                    new_enemies.append(e)
                if consume:
                    hit = True
            else:
                new_enemies.append(e)
        state.enemies = new_enemies
        if not hit:
            alive_proj.append(proj)

    state.projectiles = alive_proj

    state.enemies = [e for e in state.enemies if e.hp > 0]

    _update_enemy_bullets(state, dt)
    _blood_pact_tick(state, dt)


def _blood_pact_tick(state: GameState, dt: float) -> None:
    stacks = state.upgrade_counts.get("blood_pact", 0)
    if stacks <= 0:
        return
    drain = 0.35 * stacks * dt
    state.player.hp = max(1.0, state.player.hp - drain)


def _update_enemy_bullets(state: GameState, dt: float) -> None:
    p = state.player
    alive = []
    for b in state.enemy_bullets:
        b["x"] += b["vx"] * dt
        b["y"] += b["vy"] * dt
        b["life"] -= dt
        if b["life"] <= 0:
            continue
        if math.hypot(b["x"] - p.x, b["y"] - p.y) <= p.radius + 6:
            p.take_damage(b["dmg"])
            state.damage_flash = min(0.85, state.damage_flash + 0.25)
            continue
        alive.append(b)
    state.enemy_bullets = alive
