"""
Criação / reaplicação da janela ou ecrã completo.
"""

from __future__ import annotations

from typing import Tuple

import pygame

from core import config


def apply_video_mode(width: int, height: int, fullscreen: bool) -> pygame.Surface:
    width = max(320, int(width))
    height = max(240, int(height))
    flags = 0
    if fullscreen:
        flags |= pygame.FULLSCREEN
        try:
            flags |= pygame.SCALED
        except AttributeError:
            pass
    screen = pygame.display.set_mode((width, height), flags)
    config.set_viewport(*screen.get_size())
    return screen


def toggle_fullscreen(
    current: Tuple[int, int], want_fullscreen: bool
) -> pygame.Surface:
    w, h = current
    return apply_video_mode(w, h, want_fullscreen)
