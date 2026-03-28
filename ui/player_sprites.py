"""
Sprites do jogador: parado (frente) e 2 frames de caminhada (perfil).
Ficheiros: player_idle.png, player_walk.png, player_walk_2.png (opcional — duplica frame 1 se faltar).
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import pygame

from core import config


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _prepare_surface(surf: pygame.Surface) -> pygame.Surface:
    """Escala para altura fixa. Fundo branco: chroma só se o canto for opaco."""
    surf = surf.convert_alpha()
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
    Devolve (idle, [walk_a, walk_b]) ou (None, None) se idle ou primeiro walk em falta.
    """
    root = _project_root()
    idle_p = root / "assets" / "sprites" / "player_idle.png"
    walk_p = root / "assets" / "sprites" / "player_walk.png"
    walk2_p = root / "assets" / "sprites" / "player_walk_2.png"
    if not idle_p.is_file() or not walk_p.is_file():
        return None, None
    try:
        idle = _prepare_surface(pygame.image.load(str(idle_p)))
        w1 = _prepare_surface(pygame.image.load(str(walk_p)))
        if walk2_p.is_file():
            w2 = _prepare_surface(pygame.image.load(str(walk2_p)))
            walks: List[pygame.Surface] = [w1, w2]
        else:
            walks = [w1, w1]
        return idle, walks
    except (pygame.error, OSError):
        return None, None
