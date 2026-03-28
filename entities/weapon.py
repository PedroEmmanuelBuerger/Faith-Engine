"""
Definição de armas: stats, comportamento de ataque e registo global.
O disparo concreto continua em systems.weapon_system (projéteis, arcos, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from core.game_state import GameState


class AttackBehavior(Enum):
    """Tipo lógico de ataque (UI / extensões futuras)."""

    PROJECTILE_MOUSE = auto()
    MELEE_ARC = auto()
    MELEE_LINE = auto()
    AREA_SELF = auto()
    ORBITAL = auto()


# IDs alinhados com cartas de upgrade
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

MAX_LOADOUT_WEAPONS = 3
WEAPON_IDS: frozenset[str] = frozenset(WEAPON_ORDER)


@dataclass(frozen=True)
class Weapon:
    id: str
    name: str
    damage_multiplier: float
    range_units: float
    attack_speed_multiplier: float
    sprite_key: str
    behavior: AttackBehavior

    def attack(self, state: GameState) -> None:
        from systems import weapon_system

        weapon_system.dispatch_weapon_attack(self.id, state)


_REGISTRY: Dict[str, Weapon] = {}


def _register_all() -> None:
    global _REGISTRY
    defs = (
        Weapon(
            W_DARK_BOLT,
            "Raio Sombrio",
            1.0,
            420.0,
            1.0,
            "staff",
            AttackBehavior.PROJECTILE_MOUSE,
        ),
        Weapon(
            W_RITUAL_SWORD,
            "Espada Ritual",
            1.0,
            72.0,
            1.0,
            "sword",
            AttackBehavior.MELEE_ARC,
        ),
        Weapon(
            W_SERPENT_WHIP,
            "Chicote da Serpente",
            1.0,
            180.0,
            1.05,
            "whip",
            AttackBehavior.MELEE_LINE,
        ),
        Weapon(
            W_HOLY_WATER,
            "Água Benta",
            1.0,
            300.0,
            0.92,
            "holy_water",
            AttackBehavior.PROJECTILE_MOUSE,
        ),
        Weapon(
            W_INFERNO_PULSE,
            "Pulso Infernal",
            1.0,
            110.0,
            0.55,
            "tome",
            AttackBehavior.AREA_SELF,
        ),
        Weapon(
            W_CELESTIAL_ORBS,
            "Orbes Celestiais",
            1.0,
            80.0,
            1.0,
            "orb",
            AttackBehavior.ORBITAL,
        ),
    )
    _REGISTRY = {w.id: w for w in defs}


_register_all()


def get_weapon(weapon_id: str) -> Weapon:
    return _REGISTRY.get(weapon_id) or _REGISTRY[W_DARK_BOLT]


def compute_active_weapon(state: GameState) -> str:
    """Arma com mais pilhas; empate: ordem em WEAPON_ORDER."""
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
