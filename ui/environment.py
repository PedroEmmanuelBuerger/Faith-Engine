"""
Chão procedural (chunks) — delegado a ChunkWorld no GameState.
"""

from __future__ import annotations

import pygame

from core.game_state import GameState


def draw_world_background(surface: pygame.Surface, state: GameState) -> None:
    state.world.draw(surface, state.camera_x, state.camera_y)
