"""
Cartas de upgrade empilháveis + sinergias (dados + aplicação ao estado).
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from core.game_state import GameState

UPGRADE_DEFS: Dict[str, Tuple[str, str]] = {
    "dark_chant": ("Canto Obscuro", "+20% geração de Fé por pilha."),
    "blood_ritual": ("Ritual de Sangue", "+10% dano dos projéteis por pilha."),
    "mad_prophet": (
        "Profeta Louco",
        "A cada ~5s um efeito aleatório (dano projétil, velocidade, Fé ou cura).",
    ),
    "void_echo": ("Eco do Vazio", "+6% velocidade dos projéteis por pilha."),
    "cult_network": ("Rede do Culto", "+0,8 Fé/s passiva por seguidor acumulado."),
    "rapid_pulse": ("Pulso Rápido", "Cadência de tiro ~8% mais rápida por pilha."),
    "martyr_blood": ("Sangue do Mártir", "+12 HP máximos e +3 cura ao escolher."),
}


def all_upgrade_ids() -> List[str]:
    return list(UPGRADE_DEFS.keys())


def describe(uid: str) -> Tuple[str, str]:
    return UPGRADE_DEFS[uid]


def random_choices(n: int = 3, exclude: Optional[List[str]] = None) -> List[str]:
    pool = [u for u in all_upgrade_ids() if not exclude or u not in exclude]
    if len(pool) < n:
        return pool[:]
    return random.sample(pool, n)


def refresh_stats(state: GameState) -> None:
    p = state.player
    c = state.upgrade_counts

    faith_from_upgrades = 1.0 + 0.20 * c.get("dark_chant", 0)
    dmg = 1.0 + 0.10 * c.get("blood_ritual", 0)
    proj_spd = 1.0 + 0.06 * c.get("void_echo", 0)

    if c.get("dark_chant", 0) > 0 and c.get("blood_ritual", 0) > 0:
        dmg *= 1.15
        state.synergy_zeal_active = True
    else:
        state.synergy_zeal_active = False

    interval_mult = 0.92 ** c.get("rapid_pulse", 0)

    p.damage_multiplier = dmg
    p.projectile_speed_mult = proj_spd
    p.shoot_interval = max(0.12, 0.38 * interval_mult)

    state.followers = 1.0 + c.get("cult_network", 0) * 0.8
    state.faith_rate_multiplier = faith_from_upgrades * state.prestige_faith_mult
    state.mad_prophet_stacks = c.get("mad_prophet", 0)


def on_pick_martyr_blood(state: GameState) -> None:
    state.player.max_hp += 12
    state.player.hp = min(state.player.hp + 3, state.player.max_hp)


_ON_PICK: Dict[str, Callable[[GameState], None]] = {
    "martyr_blood": on_pick_martyr_blood,
}


def apply_upgrade(state: GameState, uid: str) -> None:
    state.upgrade_counts[uid] = state.upgrade_counts.get(uid, 0) + 1
    if uid in _ON_PICK:
        _ON_PICK[uid](state)
    refresh_stats(state)
