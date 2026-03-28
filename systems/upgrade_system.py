"""
Cartas do Culto do Infinito: armas, habilidades e apoios leves.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

from systems import synergies
from systems.weapon_system import (
    W_CELESTIAL_ORBS,
    W_DARK_BOLT,
    W_HOLY_WATER,
    W_INFERNO_PULSE,
    W_RITUAL_SWORD,
    W_SERPENT_WHIP,
    WEAPON_ORDER,
)

if TYPE_CHECKING:
    from core.game_state import GameState

# (nome, descrição clara do efeito)
UPGRADE_DEFS: Dict[str, Tuple[str, str]] = {
    # —— Armas (uma “ganha” por pilha maior; empilhar melhora a arma escolhida)
    "w_dark_bolt": (
        "Raio Sombrio",
        "Projétil rápido ao inimigo mais próximo. Empilha: mais cadência implícita com outras cartas.",
    ),
    "w_ritual_sword": (
        "Espada Ritual",
        "Golpe em arco à frente — acerta vários inimigos de uma vez. Pilhas: mais alcance e arco.",
    ),
    "w_serpent_whip": (
        "Chicote da Serpente",
        "Açoite em linha longa. Pilhas: mais comprimento.",
    ),
    "w_holy_water": (
        "Água Benta",
        "Lança um frasco; ao impacto fica um poço sagrado no chão que queima ao passar.",
    ),
    "w_inferno_pulse": (
        "Pulso Infernal",
        "Explosão circular em volta de ti. Pilhas: raio maior. Cadência mais lenta.",
    ),
    "w_celestial_orbs": (
        "Orbes Celestiais",
        "Esferas giram à tua volta e ferem ao contacto. Sem projétil: puro corpo-a-corpo orbital.",
    ),
    # —— Habilidades (mecânicas)
    "flame_ritual": (
        "Ritual das Chamas",
        "Cada morte causa uma pequena explosão de fogo (dano em área).",
    ),
    "chain_lightning": (
        "Corrente Elétrica",
        "Acertos de Raio Sombrio saltam a inimigos vizinhos (ricochete).",
    ),
    "blood_pact": (
        "Pacto de Sangue",
        "Perdes vida lentamente mas o teu dano de armas dispara muito.",
    ),
    "possession_hex": (
        "Hex da Possessão",
        "Chance ao acertar: inimigo fica confuso e deixa de te perseguir por uns segundos.",
    ),
    "echo_shot": (
        "Eco do Disparo",
        "O Raio Sombrio dispara um segundo projétil ligeiramente desviado.",
    ),
    # —— Apoios leves (secundários)
    "cult_network": (
        "Rede de Fiéis",
        "Um pouco mais de Fé passiva (incremental).",
    ),
    "fervor": (
        "Fervor",
        "Cadência de ataque principal ligeiramente mais rápida.",
    ),
    "veil_step": (
        "Passo do Véu",
        "Movimento um pouco mais rápido; sinergia com Orbes.",
    ),
    "venom_font": (
        "Fonte Venenosa",
        "Sinergia: com Água Benta, os poços causam mais dano e duram mais.",
    ),
    "omen_sight": (
        "Olho do Presságio",
        "A cada poucos segundos: bónus breve de dano, velocidade de projétil, Fé ou cura.",
    ),
    "martyr_vein": (
        "Veia do Mártir",
        "Ao escolher: +14 HP máx. e cura imediata pequena.",
    ),
}

UPGRADE_ICONS: Dict[str, str] = {
    "w_dark_bolt": "⚡",
    "w_ritual_sword": "⚔",
    "w_serpent_whip": "〰",
    "w_holy_water": "💧",
    "w_inferno_pulse": "🔥",
    "w_celestial_orbs": "✦",
    "flame_ritual": "🜂",
    "chain_lightning": "⟡",
    "blood_pact": "🩸",
    "possession_hex": "👁",
    "echo_shot": "◇",
    "cult_network": "◎",
    "fervor": "✧",
    "veil_step": "☍",
    "venom_font": "☠",
    "omen_sight": "🔮",
    "martyr_vein": "✚",
}


def icon_for(uid: str) -> str:
    return UPGRADE_ICONS.get(uid, "✦")


def all_upgrade_ids() -> List[str]:
    return list(UPGRADE_DEFS.keys())


def describe(uid: str) -> Tuple[str, str]:
    return UPGRADE_DEFS[uid]


def random_choices(n: int = 3, exclude: Optional[List[str]] = None) -> List[str]:
    pool = [u for u in all_upgrade_ids() if not exclude or u not in exclude]
    if len(pool) < n:
        return pool[:]
    return random.sample(pool, n)


def compute_active_weapon(state: GameState) -> str:
    """Arma com mais pilhas; empate: ordem em WEAPON_ORDER (último na lista perde desempate)."""
    c = state.upgrade_counts
    best = -1
    wid = W_DARK_BOLT
    for w in WEAPON_ORDER:
        n = c.get(w, 0)
        if n > best:
            best = n
            wid = w
    if best <= 0:
        return W_DARK_BOLT
    return wid


def refresh_stats(state: GameState) -> None:
    p = state.player
    c = state.upgrade_counts

    state.active_weapon_id = compute_active_weapon(state)

    # Dano: pacto de sangue é o grosso; resto mínimo
    pact = c.get("blood_pact", 0)
    state.weapon_damage_mult = 1.0 + pact * 0.42 + 0.04 * max(0, c.get("fervor", 0))

    p.damage_multiplier = 1.0 + 0.03 * c.get("fervor", 0)
    p.projectile_speed_mult = 1.0 + 0.04 * c.get("veil_step", 0)
    p.move_speed = 240.0 + 8 * c.get("veil_step", 0)

    interval = max(0.1, 0.95 * (0.9 ** c.get("fervor", 0)))
    p.shoot_interval = interval

    state.followers = 1.0 + c.get("cult_network", 0) * 0.7
    state.faith_rate_multiplier = (1.0 + 0.06 * c.get("cult_network", 0)) * state.prestige_faith_mult

    state.mad_prophet_stacks = c.get("omen_sight", 0)

    synergies.refresh_synergy_flags(state)


def on_pick_martyr_vein(state: GameState) -> None:
    state.player.max_hp += 14
    state.player.hp = min(state.player.hp + 6, state.player.max_hp)


_ON_PICK: Dict[str, Callable[[GameState], None]] = {
    "martyr_vein": on_pick_martyr_vein,
}


def apply_upgrade(state: GameState, uid: str) -> None:
    state.upgrade_counts[uid] = state.upgrade_counts.get(uid, 0) + 1
    if uid in _ON_PICK:
        _ON_PICK[uid](state)
    refresh_stats(state)
