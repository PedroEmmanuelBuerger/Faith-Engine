"""
Agitação e flashes de ecrã — valores consumidos pelo GameState / loop principal.
"""


def trigger_hit_reaction(state, shake: float = 8.0, flash: float = 0.35) -> None:
    """Chamado quando o jogador ou o combate pedem impacto visual."""
    state.screen_shake = max(state.screen_shake, shake)
    state.damage_flash = min(0.95, state.damage_flash + flash)
