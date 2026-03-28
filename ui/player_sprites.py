"""
Sprites do jogador: parado (frente) e 2 frames de caminhada (perfil).
Ficheiros: player_idle.png, player_walk.png, player_walk_2.png (opcional — duplica frame 1 se faltar).
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from core import config
from ui.sprite_assets import load_player_sprites_dynamic


def _prepare_surface(surf: pygame.Surface) -> pygame.Surface:
    """Escala para altura fixa. Fundo branco: chroma só se o canto for opaco."""
    try:
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            surf = surf.convert_alpha()
    except pygame.error:
        pass
    c0 = surf.get_at((0, 0))
    a = c0[3] if len(c0) > 3 else 255
    if a >= 250:
        surf.set_colorkey((255, 255, 255))
    h, w = surf.get_height(), surf.get_width()
    target_h = config.PLAYER_SPRITE_HEIGHT
    if h <= 0:
        return surf
    scale = target_h / h
    nw = max(1, int(w * scale))
    nh = max(1, int(h * scale))
    try:
        return pygame.transform.smoothscale(surf, (nw, nh))
    except Exception:
        return pygame.transform.scale(surf, (nw, nh))


def load_player_sprites() -> Tuple[
    Optional[pygame.Surface], Optional[List[pygame.Surface]]
]:
    """
    assets/sprites/player/ (sprite.png, idle.png, walk.png, …) ou legacy na raiz de sprites/.
    Devolve (idle, [walk_a, walk_b]) ou (None, None) se incompleto.
    """
    raw_idle, raw_walks = load_player_sprites_dynamic()
    if raw_idle is None or not raw_walks:
        return None, None
    try:
        idle = _prepare_surface(raw_idle)
        walks = [_prepare_surface(w) for w in raw_walks]
        return idle, walks
    except (pygame.error, OSError, ValueError):
        return None, None
