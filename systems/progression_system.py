"""
XP, níveis, menu de upgrades e tick do Profeta Louco.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from systems import upgrade_system

if TYPE_CHECKING:
    from core.game_state import GameState


def recalc_xp_to_next(state: GameState) -> None:
    state.xp_to_next = int(28 * (1.2 ** (state.level - 1)))


def grant_xp(state: GameState, amount: float) -> None:
    if state.level_up_paused or state.player.hp <= 0:
        return
    state.xp += amount
    try_level_up(state)


def try_level_up(state: GameState) -> None:
    if state.xp < state.xp_to_next:
        return
    state.xp -= state.xp_to_next
    state.level += 1
    recalc_xp_to_next(state)
    state.level_up_paused = True
    state.upgrade_choice_ids = upgrade_system.random_choices(3)
    state.upgrade_choice_rarities = upgrade_system.roll_rarities(len(state.upgrade_choice_ids))


def select_upgrade(state: GameState, index: int) -> None:
    if not state.level_up_paused:
        return
    if index < 0 or index >= len(state.upgrade_choice_ids):
        return
    uid = state.upgrade_choice_ids[index]
    rarities = getattr(state, "upgrade_choice_rarities", [])
    rarity = (
        rarities[index]
        if index < len(rarities)
        else upgrade_system.RARITY_COMMON
    )
    upgrade_system.apply_upgrade(state, uid, rarity=rarity)
    state.upgrade_choice_ids = []
    state.upgrade_choice_rarities = []
    state.level_up_paused = False
    try_level_up(state)


def tick_mad_prophet(state: GameState, dt: float) -> None:
    state._prophet_dmg_left = max(0.0, state._prophet_dmg_left - dt)
    state._prophet_spd_left = max(0.0, state._prophet_spd_left - dt)

    stacks = state.mad_prophet_stacks
    if stacks <= 0:
        state.mad_prophet_timer = 0.0
        return

    state.mad_prophet_timer += dt
    interval = 5.0 / (1.0 + 0.25 * max(0, stacks - 1))
    if state.mad_prophet_timer < interval:
        return
    state.mad_prophet_timer = 0.0

    roll = random.choice(("dmg", "speed", "faith", "heal"))
    if roll == "dmg":
        state._prophet_dmg_left = 2.8
    elif roll == "speed":
        state._prophet_spd_left = 2.8
    elif roll == "faith":
        state.faith += 12 + stacks * 4
    else:
        state.player.hp = min(state.player.max_hp, state.player.hp + 10 + stacks * 2)


def wave_interval_seconds(state: GameState) -> float:
    from core import config as gc

    return gc.WAVE_ADVANCE_INTERVAL_BASE + random.uniform(-5.0, 9.0)


def advance_wave(state: GameState) -> None:
    """Avança a onda por tempo; ondas múltiplas de 5 iniciam combate de chefe."""
    if getattr(state, "in_boss_fight", False):
        return
    state.wave = min(99, state.wave + 1)
    state.wave_timer = wave_interval_seconds(state)
    if state.wave % 5 == 0:
        from systems import spawn_system

        spawn_system.begin_boss_wave(state)
