"""
Sinergias entre tags de upgrades (fogo + explosão, orbs + velocidade, etc.).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_state import GameState


def refresh_synergy_flags(state: GameState) -> None:
    """Atualiza multiplicadores e flags usados por armas e efeitos."""
    c = state.upgrade_counts

    # Fogo + explosão: rajadas e mortes com chama maiores
    state.synergy_inferno = (
        c.get("flame_ritual", 0) > 0
        and (
            c.get("w_inferno_pulse", 0) > 0
            or c.get("flame_ritual", 0) >= 2
        )
    )
    state.synergy_explosion_radius_mult = (
        1.45 if state.synergy_inferno else 1.0
    )

    # Água benta + veneno: poços com mais dano e duração
    state.synergy_toxic_baptism = (
        c.get("w_holy_water", 0) > 0 and c.get("venom_font", 0) > 0
    )
    state.synergy_pool_dps_mult = 1.55 if state.synergy_toxic_baptism else 1.0
    state.synergy_pool_duration_bonus = 1.4 if state.synergy_toxic_baptism else 1.0

    # Orbs + passo veloz (cadência / rotação)
    state.synergy_orb_velocity = (
        1.0 + 0.22 * c.get("w_celestial_orbs", 0) * c.get("veil_step", 0)
    )

    # Corrente + eco (raio salta mais vezes)
    state.synergy_chain_echo = (
        c.get("chain_lightning", 0) > 0 and c.get("echo_shot", 0) > 0
    )
    state.chain_bonus_jumps = (
        1 + int(state.synergy_chain_echo)
    )

    # Legado UI: texto de sinergia no menu de nível
    state.synergy_zeal_active = (
        c.get("blood_pact", 0) > 0 and c.get("w_dark_bolt", 0) >= 2
    )
