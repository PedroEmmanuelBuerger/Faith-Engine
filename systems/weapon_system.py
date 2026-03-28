"""
Armas: até 3 no loadout, cooldowns independentes, mira rato ou auto (inimigo visível mais próximo).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Tuple

from core import config, sfx, utils
from entities.enemy import Enemy
from entities.projectile import Projectile
from entities.weapon import (
    W_CELESTIAL_ORBS,
    W_DARK_BOLT,
    W_HOLY_WATER,
    W_INFERNO_PULSE,
    W_RITUAL_SWORD,
    W_SERPENT_WHIP,
    get_weapon,
)
from effects import particles as particle_fx

if TYPE_CHECKING:
    from core.game_state import GameState

_SCREEN_MARGIN = 64.0


def weapon_tier(state: GameState, wid: str) -> int:
    return max(0, state.upgrade_counts.get(wid, 0))


def _enemy_on_screen(state: GameState, e: Enemy) -> bool:
    if e.hp <= 0:
        return False
    sx, sy = utils.world_to_screen(e.x, e.y, state.camera_x, state.camera_y)
    m = _SCREEN_MARGIN
    return -m <= sx <= config.VIEWPORT_W + m and -m <= sy <= config.VIEWPORT_H + m


def _direction_from_mouse(state: GameState) -> Tuple[float, float]:
    p = state.player
    dx = state.aim_world_x - p.x
    dy = state.aim_world_y - p.y
    d = math.hypot(dx, dy)
    if d < 8.0:
        return (1.0, 0.0) if p.facing_right else (-1.0, 0.0)
    return dx / d, dy / d


def _direction_nearest_visible(state: GameState) -> Tuple[float, float]:
    p = state.player
    visible = [e for e in state.enemies if _enemy_on_screen(state, e)]
    if not visible:
        return _direction_from_mouse(state)
    best = min(visible, key=lambda e: (e.x - p.x) ** 2 + (e.y - p.y) ** 2)
    dx, dy = best.x - p.x, best.y - p.y
    d = math.hypot(dx, dy)
    if d < 1e-3:
        return _direction_from_mouse(state)
    return dx / d, dy / d


def _aim_direction(state: GameState) -> Tuple[float, float]:
    if state.auto_attack_enabled:
        return _direction_nearest_visible(state)
    return _direction_from_mouse(state)


def _weapon_feedback(state: GameState) -> None:
    p = state.player
    p.weapon_visual_kick = min(1.0, p.weapon_visual_kick + 0.45)


def _base_dmg_for_weapon(state: GameState, wid: str) -> float:
    w = get_weapon(wid)
    return (
        state.player.effective_damage
        * state.prophet_projectile_damage_mult()
        * state.weapon_damage_mult
        * w.damage_multiplier
    )


def _set_weapon_cooldown(state: GameState, wid: str, factor: float = 1.0) -> None:
    p = state.player
    gw = get_weapon(wid)
    dur = max(0.08, p.shoot_interval / max(0.25, gw.attack_speed_multiplier) * factor)
    state.weapon_cooldowns[wid] = dur


def fire_dark_bolt(state: GameState, firing_wid: str) -> None:
    p = state.player
    ux, uy = _aim_direction(state)
    visible = [e for e in state.enemies if _enemy_on_screen(state, e)]
    if not visible:
        state.weapon_cooldowns[firing_wid] = 0.12
        return
    spd = p.projectile_speed * state.prophet_projectile_speed_mult()
    sx = p.x + ux * (p.radius + 4)
    sy = p.y + uy * (p.radius + 4)
    bounces = state.upgrade_counts.get("chain_lightning", 0) + (
        state.chain_bonus_jumps if state.synergy_chain_echo else 0
    )
    w = get_weapon(firing_wid)
    bd = _base_dmg_for_weapon(state, firing_wid)
    proj = Projectile(
        sx,
        sy,
        ux,
        uy,
        spd,
        bd,
        radius=6.0,
        max_range=min(420.0, w.range_units),
        kind="bolt",
        bounces_remaining=bounces,
        pierce_remaining=0,
    )
    state.projectiles.append(proj)
    _set_weapon_cooldown(state, firing_wid)
    _weapon_feedback(state)
    sfx.play_shoot()
    particle_fx.spawn_muzzle(state, sx, sy, ux, uy)
    if firing_wid == W_DARK_BOLT and state.upgrade_counts.get("echo_shot", 0) > 0:
        ang = 0.28
        ca, sa = math.cos(ang), math.sin(ang)
        rdx = ux * ca - uy * sa
        rdy = ux * sa + uy * ca
        state.projectiles.append(
            Projectile(
                sx,
                sy,
                rdx,
                rdy,
                spd * 0.92,
                bd * 0.72,
                radius=5.0,
                max_range=min(380.0, w.range_units * 0.9),
                kind="bolt",
                bounces_remaining=max(0, bounces - 1),
                pierce_remaining=0,
            )
        )


def fire_ritual_sword(state: GameState, firing_wid: str) -> None:
    p = state.player
    visible = [e for e in state.enemies if _enemy_on_screen(state, e)]
    if not visible:
        state.weapon_cooldowns[firing_wid] = 0.12
        return
    ux, uy = _aim_direction(state)
    ang = math.atan2(uy, ux)
    arc = 1.35 + 0.08 * weapon_tier(state, firing_wid)
    w = get_weapon(firing_wid)
    rng = min(w.range_units, 58 + weapon_tier(state, firing_wid) * 5)
    state.melee_swings.append(
        {
            "t": 0.0,
            "duration": 0.11,
            "angle": ang,
            "half_arc": arc / 2,
            "range": rng,
            "dmg": _base_dmg_for_weapon(state, firing_wid) * 1.35,
            "hit": set(),
        }
    )
    _set_weapon_cooldown(state, firing_wid)
    _weapon_feedback(state)
    sfx.play_shoot_heavy()
    state.screen_shake = max(state.screen_shake, 2.4)
    particle_fx.spawn_arc_slash(state, p.x, p.y, ang, rng)


def fire_serpent_whip(state: GameState, firing_wid: str) -> None:
    p = state.player
    visible = [e for e in state.enemies if _enemy_on_screen(state, e)]
    if not visible:
        state.weapon_cooldowns[firing_wid] = 0.12
        return
    ux, uy = _aim_direction(state)
    w = get_weapon(firing_wid)
    length = min(w.range_units, 150 + weapon_tier(state, firing_wid) * 12)
    state.whip_strikes.append(
        {
            "t": 0.0,
            "duration": 0.09,
            "ux": ux,
            "uy": uy,
            "length": length,
            "width": 36.0,
            "dmg": _base_dmg_for_weapon(state, firing_wid) * 1.15,
            "hit": set(),
        }
    )
    _set_weapon_cooldown(state, firing_wid)
    _weapon_feedback(state)
    sfx.play_shoot_heavy()
    state.screen_shake = max(state.screen_shake, 2.0)
    particle_fx.spawn_whip_line(state, p.x, p.y, ux, uy, length)


def fire_holy_water(state: GameState, firing_wid: str) -> None:
    p = state.player
    visible = [e for e in state.enemies if _enemy_on_screen(state, e)]
    if not visible:
        state.weapon_cooldowns[firing_wid] = 0.12
        return
    ux, uy = _aim_direction(state)
    spd = 280 * p.projectile_speed_mult
    sx = p.x + ux * (p.radius + 6)
    sy = p.y + uy * (p.radius + 6)
    w = get_weapon(firing_wid)
    state.projectiles.append(
        Projectile(
            sx,
            sy,
            ux,
            uy,
            spd,
            _base_dmg_for_weapon(state, firing_wid) * 0.55,
            radius=8.0,
            max_range=min(300.0, w.range_units),
            kind="holy_flask",
            spawns_pool=True,
        )
    )
    _set_weapon_cooldown(state, firing_wid, 1.15)
    _weapon_feedback(state)
    sfx.play_shoot()


def fire_inferno_pulse(state: GameState, firing_wid: str) -> None:
    p = state.player
    w = get_weapon(firing_wid)
    rad = (95 + weapon_tier(state, firing_wid) * 8) * state.synergy_explosion_radius_mult
    rad = min(rad, w.range_units * 1.2)
    dmg = _base_dmg_for_weapon(state, firing_wid) * 0.95
    state.pending_radial_pulses.append({"t": 0.0, "radius": rad, "dmg": dmg, "max_t": 0.14})
    asp = max(0.25, w.attack_speed_multiplier)
    dur = max(0.55, p.shoot_interval * 1.6 / asp)
    state.weapon_cooldowns[firing_wid] = dur
    _weapon_feedback(state)
    particle_fx.spawn_fire_ring(state, p.x, p.y, rad)
    sfx.play_shoot_heavy()
    state.screen_shake = max(state.screen_shake, 5.2 + min(4.0, rad * 0.018))
    _damage_in_radius(state, p.x, p.y, rad, dmg, "inferno")


def dispatch_weapon_attack(wid: str, state: GameState) -> None:
    if wid == W_RITUAL_SWORD:
        fire_ritual_sword(state, wid)
    elif wid == W_SERPENT_WHIP:
        fire_serpent_whip(state, wid)
    elif wid == W_HOLY_WATER:
        fire_holy_water(state, wid)
    elif wid == W_INFERNO_PULSE:
        fire_inferno_pulse(state, wid)
    elif wid == W_CELESTIAL_ORBS:
        p = state.player
        _set_weapon_cooldown(state, wid, 1.35)
        _weapon_feedback(state)
        sfx.play_shoot()
        particle_fx.spawn_fire_ring(
            state, p.x, p.y, 48 + weapon_tier(state, W_CELESTIAL_ORBS) * 4
        )
    else:
        fire_dark_bolt(state, wid)


def tick_weapon_cooldowns(state: GameState, dt: float) -> None:
    for wid in state.weapon_loadout:
        cur = state.weapon_cooldowns.get(wid, 0.0)
        if cur > 0:
            state.weapon_cooldowns[wid] = max(0.0, cur - dt)


def try_fire_all_weapons(state: GameState) -> None:
    p = state.player
    if p.hp <= 0:
        return
    for wid in state.weapon_loadout:
        if state.weapon_cooldowns.get(wid, 0.0) > 0:
            continue
        if weapon_tier(state, wid) <= 0 and wid != W_DARK_BOLT:
            continue
        get_weapon(wid).attack(state)


def update_celestial_orbs(state: GameState, dt: float) -> None:
    tier = weapon_tier(state, W_CELESTIAL_ORBS)
    if tier <= 0:
        return
    n = 2 + min(4, tier)
    base_r = 64 + tier * 5
    spd = (1.9 + tier * 0.12) * state.synergy_orb_velocity
    state.orbital_phase += dt * spd
    p = state.player
    orbs = []
    for i in range(n):
        ang = state.orbital_phase + (math.tau / n) * i
        ox = p.x + math.cos(ang) * base_r
        oy = p.y + math.sin(ang) * base_r
        orbs.append((ox, oy))
    state.orbital_debug = orbs
    odmg = _base_dmg_for_weapon(state, W_CELESTIAL_ORBS) * 0.22 * (1 + 0.06 * tier)
    hit_r = 16.0
    from systems import combat_system

    for ox, oy in orbs:
        for e in list(state.enemies):
            if e.hp <= 0:
                continue
            if math.hypot(e.x - ox, e.y - oy) <= hit_r + e.radius:
                combat_system.apply_weapon_hit(state, e, odmg * dt * 18, "orb")


def update_melee_swings(state: GameState, dt: float) -> None:
    p = state.player
    alive = []
    for sw in state.melee_swings:
        sw["t"] += dt
        if sw["t"] >= sw["duration"]:
            continue
        ang = sw["angle"]
        ha = sw["half_arc"]
        rng = sw["range"]
        for e in state.enemies:
            if e.hp <= 0 or id(e) in sw["hit"]:
                continue
            dx, dy = e.x - p.x, e.y - p.y
            d = math.hypot(dx, dy)
            if d > rng + e.radius:
                continue
            a = math.atan2(dy, dx)
            da = (a - ang + math.pi) % math.tau - math.pi
            if abs(da) <= ha + 0.25:
                sw["hit"].add(id(e))
                from systems import combat_system

                combat_system.apply_weapon_hit(state, e, sw["dmg"], "sword")
        alive.append(sw)
    state.melee_swings = alive


def update_whip_strikes(state: GameState, dt: float) -> None:
    p = state.player
    alive = []
    for w in state.whip_strikes:
        w["t"] += dt
        if w["t"] >= w["duration"]:
            continue
        ux, uy = w["ux"], w["uy"]
        length, width = w["length"], w["width"]
        for e in state.enemies:
            if e.hp <= 0 or id(e) in w["hit"]:
                continue
            dx, dy = e.x - p.x, e.y - p.y
            t = dx * ux + dy * uy
            if t < 0 or t > length + e.radius:
                continue
            px, py = p.x + ux * min(t, length), p.y + uy * min(t, length)
            dist = math.hypot(e.x - px, e.y - py)
            if dist <= width / 2 + e.radius:
                w["hit"].add(id(e))
                from systems import combat_system

                combat_system.apply_weapon_hit(state, e, w["dmg"], "whip")
        alive.append(w)
    state.whip_strikes = alive


def update_radial_pulse_visual(state: GameState, dt: float) -> None:
    alive = []
    for pulse in state.pending_radial_pulses:
        pulse["t"] += dt
        if pulse["t"] < pulse["max_t"]:
            alive.append(pulse)
    state.pending_radial_pulses = alive


def _damage_in_radius(
    state: GameState, x: float, y: float, radius: float, dmg: float, tag: str
) -> None:
    from systems import combat_system

    for e in list(state.enemies):
        if e.hp <= 0:
            continue
        if math.hypot(e.x - x, e.y - y) <= radius + e.radius:
            combat_system.apply_weapon_hit(state, e, dmg, tag)


def update_ground_pools(state: GameState, dt: float) -> None:
    p = state.player
    pools = []
    for pool in state.ground_pools:
        pool["t"] -= dt
        pool["acc"] = pool.get("acc", 0.0) + dt
        dps = pool["dps"] * state.synergy_pool_dps_mult
        tick = 0.18
        while pool["acc"] >= tick:
            pool["acc"] -= tick
            from systems import combat_system

            for e in list(state.enemies):
                if e.hp <= 0:
                    continue
                if math.hypot(e.x - pool["x"], e.y - pool["y"]) <= pool["radius"] + e.radius:
                    combat_system.apply_weapon_hit(state, e, dps * tick * 1.1, "pool")
        if pool["t"] > 0:
            pools.append(pool)
    state.ground_pools = pools


def spawn_holy_pool(state: GameState, x: float, y: float) -> None:
    dur = 3.6 * state.synergy_pool_duration_bonus
    dps = 9.0 + weapon_tier(state, W_HOLY_WATER) * 1.2
    state.ground_pools.append(
        {
            "x": x,
            "y": y,
            "radius": 52 + weapon_tier(state, W_HOLY_WATER) * 4,
            "t": dur,
            "dps": dps,
            "acc": 0.0,
        }
    )
    particle_fx.spawn_holy_splash(state, x, y)
