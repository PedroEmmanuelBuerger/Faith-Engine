"""
Cartas do Culto do Infinito: armas, habilidades e apoios leves.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

from entities.weapon import (
    MAX_LOADOUT_WEAPONS,
    WEAPON_IDS,
    WEAPON_ORDER,
    compute_active_weapon,
    get_weapon,
)
from systems import synergies

if TYPE_CHECKING:
    from core.game_state import GameState

RARITY_COMMON = "common"
RARITY_RARE = "rare"
RARITY_EPIC = "epic"
RARITY_LEGENDARY = "legendary"

RARITY_LABEL_PT: Dict[str, str] = {
    RARITY_COMMON: "Comum",
    RARITY_RARE: "Raro",
    RARITY_EPIC: "Épico",
    RARITY_LEGENDARY: "Lendário",
}

# Cor da faixa / texto na carta (R, G, B)
RARITY_RGB: Dict[str, Tuple[int, int, int]] = {
    RARITY_COMMON: (170, 168, 188),
    RARITY_RARE: (100, 170, 255),
    RARITY_EPIC: (190, 120, 255),
    RARITY_LEGENDARY: (255, 200, 90),
}

# Bónus acumulado ao dano base do jogador (multiplicativo em refresh_stats)
RARITY_ASCENSION_BONUS: Dict[str, float] = {
    RARITY_COMMON: 0.0,
    RARITY_RARE: 0.034,
    RARITY_EPIC: 0.072,
    RARITY_LEGENDARY: 0.14,
}

# Raridade “tema” por upgrade (afeta cor mínima ao rolar)
UPGRADE_BASE_RARITY: Dict[str, str] = {
    "w_dark_bolt": RARITY_COMMON,
    "w_ritual_sword": RARITY_RARE,
    "w_serpent_whip": RARITY_COMMON,
    "w_holy_water": RARITY_RARE,
    "w_inferno_pulse": RARITY_EPIC,
    "w_celestial_orbs": RARITY_EPIC,
    "flame_ritual": RARITY_COMMON,
    "chain_lightning": RARITY_RARE,
    "blood_pact": RARITY_EPIC,
    "possession_hex": RARITY_COMMON,
    "echo_shot": RARITY_RARE,
    "cult_network": RARITY_COMMON,
    "fervor": RARITY_COMMON,
    "veil_step": RARITY_COMMON,
    "venom_font": RARITY_RARE,
    "omen_sight": RARITY_EPIC,
    "martyr_vein": RARITY_RARE,
}


def roll_rarities(n: int) -> List[str]:
    out: List[str] = []
    for _ in range(n):
        u = random.random()
        if u < 0.54:
            out.append(RARITY_COMMON)
        elif u < 0.82:
            out.append(RARITY_RARE)
        elif u < 0.95:
            out.append(RARITY_EPIC)
        else:
            out.append(RARITY_LEGENDARY)
    return out


def rarity_at_least(a: str, b: str) -> str:
    order = (RARITY_COMMON, RARITY_RARE, RARITY_EPIC, RARITY_LEGENDARY)
    return a if order.index(a) >= order.index(b) else b


def effective_rarity_for_choice(uid: str, rolled: str) -> str:
    base = UPGRADE_BASE_RARITY.get(uid, RARITY_COMMON)
    return rarity_at_least(rolled, base)


# (nome, descrição orientada ao jogador — efeito concreto)
UPGRADE_DEFS: Dict[str, Tuple[str, str]] = {
    "w_dark_bolt": (
        "Raio Sombrio",
        "Dispara um projétil rápido na direção da mira (ou do alvo em auto-ataque). Cada pilha melhora o dano base desta arma.",
    ),
    "w_ritual_sword": (
        "Espada Ritual",
        "Corta um arco à tua frente: acerta vários inimigos de uma vez. Pilhas: mais alcance e ângulo do arco.",
    ),
    "w_serpent_whip": (
        "Chicote da Serpente",
        "Açoite em linha reta e longa. Pilhas: chicote mais comprido.",
    ),
    "w_holy_water": (
        "Água Benta",
        "Arremessa um frasco; ao acertar, cria um poço sagrado no chão que causa dano contínuo a quem passa.",
    ),
    "w_inferno_pulse": (
        "Pulso Infernal",
        "Explosão circular centrada em ti. Pilhas: raio maior. Disparo mais lento que projéteis normais.",
    ),
    "w_celestial_orbs": (
        "Orbes Celestiais",
        "Orbes orbitam o teu corpo e magoam ao contacto. Precisas de pelo menos uma pilha para ativarem.",
    ),
    "flame_ritual": (
        "Ritual das Chamas",
        "Quando um inimigo morre, provoca uma pequena explosão de fogo que pode ferir outros próximos.",
    ),
    "chain_lightning": (
        "Corrente Elétrica",
        "Acertos do Raio Sombrio podem saltar para inimigos vizinhos (ricochete adicional).",
    ),
    "blood_pact": (
        "Pacto de Sangue",
        "Perdes vida continuamente, mas o dano das tuas armas aumenta muito (empilha forte com outras fontes de dano).",
    ),
    "possession_hex": (
        "Hex da Possessão",
        "Ao acertar inimigos, pequena chance de os confundir: deixam de te perseguir por uns segundos.",
    ),
    "echo_shot": (
        "Eco do Disparo",
        "O Raio Sombrio dispara um segundo projétil extra, ligeiramente desviado.",
    ),
    "cult_network": (
        "Rede de Fiéis",
        "Aumenta a Fé ganha passivamente por segundo (escala com pilhas).",
    ),
    "fervor": (
        "Fervor",
        "Aumenta ligeiramente a cadência global das armas e um pouco o teu dano corpo-a-corpo.",
    ),
    "veil_step": (
        "Passo do Véu",
        "Aumenta a velocidade de movimento e a velocidade dos projéteis; sinergia com Orbes Celestiais.",
    ),
    "venom_font": (
        "Fonte Venenosa",
        "Sinergia: com Água Benta, os poços no chão causam mais dano e duram mais tempo.",
    ),
    "omen_sight": (
        "Olho do Presságio",
        "A intervalos: recebes um bónus aleatório curto (dano, velocidade de projétil, Fé ou cura).",
    ),
    "martyr_vein": (
        "Veia do Mártir",
        "Ao escolher esta carta: +14 HP máximo e cura imediata.",
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


def _ensure_weapon_loadout(state: GameState, wid: str) -> None:
    if wid not in WEAPON_IDS:
        return
    if wid in state.weapon_loadout:
        return
    if len(state.weapon_loadout) < MAX_LOADOUT_WEAPONS:
        state.weapon_loadout.append(wid)
        return
    old = state.weapon_loadout.pop(0)
    state.upgrade_counts[old] = 0
    state.weapon_cooldowns.pop(old, None)
    state.weapon_loadout.append(wid)


def refresh_stats(state: GameState) -> None:
    p = state.player
    c = state.upgrade_counts

    state.active_weapon_id = compute_active_weapon(state)
    w = get_weapon(state.active_weapon_id)
    state.player.equipped_weapon = w

    # Dano: pacto de sangue é o grosso; resto mínimo
    pact = c.get("blood_pact", 0)
    state.weapon_damage_mult = 1.0 + pact * 0.42 + 0.04 * max(0, c.get("fervor", 0))

    asc = float(getattr(state, "ascension_pick_bonus", 0.0))
    p.damage_multiplier = (1.0 + 0.03 * c.get("fervor", 0)) * (1.0 + asc)
    p.projectile_speed_mult = 1.0 + 0.04 * c.get("veil_step", 0)
    p.move_speed = 240.0 + 8 * c.get("veil_step", 0)

    interval = max(0.1, 0.95 * (0.9 ** c.get("fervor", 0)))
    state._weapon_base_interval = interval
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


def apply_upgrade(state: GameState, uid: str, rarity: str = RARITY_COMMON) -> None:
    eff = effective_rarity_for_choice(uid, rarity)
    bonus = RARITY_ASCENSION_BONUS.get(eff, 0.0)
    state.ascension_pick_bonus = float(getattr(state, "ascension_pick_bonus", 0.0)) + bonus

    prev = state.upgrade_counts.get(uid, 0)
    if uid in WEAPON_IDS and prev == 0:
        _ensure_weapon_loadout(state, uid)
    state.upgrade_counts[uid] = prev + 1
    if uid in _ON_PICK:
        _ON_PICK[uid](state)
    refresh_stats(state)
