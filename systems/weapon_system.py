"""
Armas primárias do Culto do Infinito — cada uma altera o ritmo de combate.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Tuple

from core import config, sfx
from entities.enemy import Enemy
from entities.projectile import Projectile
from effects import particles as particle_fx

if TYPE_CHECKING:
    from core.game_state import GameState

W_DARK_BOLT = "w_dark_bolt"
W_RITUAL_SWORD = "w_ritual_sword"
W_SERPENT_WHIP = "w_serpent_whip"
W_HOLY_WATER = "w_holy_water"
W_INFERNO_PULSE = "w_inferno_pulse"
W_CELESTIAL_ORBS = "w_celestial_orbs"

WEAPON_ORDER = (
    W_INFERNO_PULSE,
    W_CELESTIAL_ORBS,
    W_HOLY_WATER,
    W_SERPENT_WHIP,
    W_RITUAL_SWORD,
    W_DARK_BOLT,
)


def weapon_tier(state: GameState, wid: str) -> int:
    return max(0, state.upgrade_counts.get(wid, 0))


def _aim_nearest(state: GameState) -> Tuple[float, float, Enemy | None]:
    p = state.player
    if not state.enemies:
        return 1.0, 0.0, None
    best = min(state.enemies, key=lambda e: (e.x - p.x) ** 2 + (e.y - p.y) ** 2)
    dx, dy = best.x - p.x, best.y - p.y
    if dx == 0 and dy == 0:
        return 1.0, 0.0, best
    return dx, dy, best


def _base_dmg(state: GameState) -> float:
    return (
        state.player.effective_damage
        * state.prophet_projectile_damage_mult()
        * state.weapon_damage_mult
    )


def fire_dark_bolt(state: GameState) -> None:
    p = state.player
    dx, dy, tgt = _aim_nearest(state)
    if tgt is None:
        return
    spd = p.projectile_speed * state.prophet_projectile_speed_mult()
    dist = math.hypot(dx, dy)
    ux, uy = dx / dist, dy / dist
    sx, sy = p.x + ux * (p.radius + 4), p.y + uy * (p.radius + 4)
    bounces = state.upgrade_counts.get("chain_lightning", 0) + (
        state.chain_bonus_jumps if state.synergy_chain_echo else 0
    )
    proj = Projectile(
        sx,
        sy,
        dx,
        dy,
        spd,
        _base_dmg(state),
        radius=6.0,
        max_range=920.0,
        kind="bolt",
        bounces_remaining=bounces,
        pierce_remaining=0,
    )
    state.projectiles.append(proj)
    p.shoot_cooldown = p.shoot_interval
    sfx.play_shoot()
    particle_fx.spawn_muzzle(state, sx, sy, ux, uy)
    if state.upgrade_counts.get("echo_shot", 0) > 0:
        ang = 0.28
        ca, sa = math.cos(ang), math.sin(ang)
        rdx = dx * ca - dy * sa
        rdy = dx * sa + dy * ca
        state.projectiles.append(
            Projectile(
                sx,
                sy,
                rdx,
                rdy,
                spd * 0.92,
                _base_dmg(state) * 0.72,
                radius=5.0,
                max_range=820.0,
                kind="bolt",
                bounces_remaining=max(0, bounces - 1),
                pierce_remaining=0,
            )
        )


def fire_ritual_sword(state: GameState) -> None:
    p = state.player
    dx, dy, tgt = _aim_nearest(state)
    ang = math.atan2(dy, dx) if tgt else 0.0
    arc = 1.35 + 0.08 * weapon_tier(state, W_RITUAL_SWORD)
    rng = 78 + weapon_tier(state, W_RITUAL_SWORD) * 6
    state.melee_swings.append(
        {
            "t": 0.0,
            "duration": 0.11,
            "angle": ang,
            "half_arc": arc / 2,
            "range": rng,
            "dmg": _base_dmg(state) * 1.35,
            "hit": set(),
        }
    )
    p.shoot_cooldown = p.shoot_interval
    sfx.play_shoot()
    particle_fx.spawn_arc_slash(state, p.x, p.y, ang, rng)


def fire_serpent_whip(state: GameState) -> None:
    p = state.player
    dx, dy, tgt = _aim_nearest(state)
    if tgt is None:
        return
    dist = math.hypot(dx, dy) or 1.0
    ux, uy = dx / dist, dy / dist
    length = 210 + weapon_tier(state, W_SERPENT_WHIP) * 18
    width = 36.0
    state.whip_strikes.append(
        {
            "t": 0.0,
            "duration": 0.09,
            "ux": ux,
            "uy": uy,
            "length": length,
            "width": width,
            "dmg": _base_dmg(state) * 1.15,
            "hit": set(),
        }
    )
    p.shoot_cooldown = p.shoot_interval
    sfx.play_shoot()
    particle_fx.spawn_whip_line(state, p.x, p.y, ux, uy, length)


def fire_holy_water(state: GameState) -> None:
    p = state.player
    dx, dy, tgt = _aim_nearest(state)
    if tgt is None:
        return
    spd = 280 * p.projectile_speed_mult
    dist = math.hypot(dx, dy) or 1.0
    ux, uy = dx / dist, dy / dist
    sx, sy = p.x + ux * (p.radius + 6), p.y + uy * (p.radius + 6)
    state.projectiles.append(
        Projectile(
            sx,
            sy,
            dx,
            dy,
            spd,
            _base_dmg(state) * 0.55,
            radius=8.0,
            max_range=480.0,
            kind="holy_flask",
            spawns_pool=True,
        )
    )
    p.shoot_cooldown = p.shoot_interval * 1.15
    sfx.play_shoot()


def fire_inferno_pulse(state: GameState) -> None:
    p = state.player
    rad = (125 + weapon_tier(state, W_INFERNO_PULSE) * 10) * state.synergy_explosion_radius_mult
    dmg = _base_dmg(state) * 0.95
    state.pending_radial_pulses.append({"t": 0.0, "radius": rad, "dmg": dmg, "max_t": 0.14})
    p.shoot_cooldown = max(0.55, p.shoot_interval * 1.6)
    particle_fx.spawn_fire_ring(state, p.x, p.y, rad)
    sfx.play_shoot()
    _damage_in_radius(state, p.x, p.y, rad, dmg, "inferno")


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
    odmg = _base_dmg(state) * 0.22 * (1 + 0.06 * tier)
    hit_r = 16.0
    from systems import combat_system

    for ox, oy in orbs:
        for e in list(state.enemies):
            if e.hp <= 0:
                continue
            if math.hypot(e.x - ox, e.y - oy) <= hit_r + e.radius:
                combat_system.apply_weapon_hit(state, e, odmg * dt * 18, "orb")


def try_primary_weapon(state: GameState) -> None:
    p = state.player
    if p.shoot_cooldown > 0 or p.hp <= 0:
        return
    wid = state.active_weapon_id
    if wid == W_RITUAL_SWORD:
        fire_ritual_sword(state)
    elif wid == W_SERPENT_WHIP:
        fire_serpent_whip(state)
    elif wid == W_HOLY_WATER:
        fire_holy_water(state)
    elif wid == W_INFERNO_PULSE:
        fire_inferno_pulse(state)
    elif wid == W_CELESTIAL_ORBS:
        # Orbes são dano contínuo; o “tiro” só regula cadência visual
        p.shoot_cooldown = p.shoot_interval * 1.35
        sfx.play_shoot()
        particle_fx.spawn_fire_ring(state, p.x, p.y, 48 + weapon_tier(state, W_CELESTIAL_ORBS) * 4)
    else:
        fire_dark_bolt(state)


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
