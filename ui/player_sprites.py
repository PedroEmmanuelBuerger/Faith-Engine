"""
Sprites do jogador: idle, caminhada, ataque e vista de costas.
Prioridade: assets/sprites/player_idle.png, player_walk.png, player_walk_2.png;
ataque/costas: player_attack.png, player_back.png (ou pasta player/).
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from core import config
from ui.procedural_sprites import (
    build_player_attack_pose,
    build_player_back_view,
    load_procedural_player_sprites,
)
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
    pygame.Surface,
    List[pygame.Surface],
    pygame.Surface,
    pygame.Surface,
]:
    """
    Sempre devolve quatro superfícies válidas (ficheiros ou procedural para lacunas).
    """
    raw_idle, raw_walks, raw_attack, raw_back = load_player_sprites_dynamic()
    if raw_idle is None or not raw_walks:
        idle, walks = load_procedural_player_sprites()
        att = _prepare_surface(build_player_attack_pose())
        back = _prepare_surface(build_player_back_view())
        return idle, walks, att, back

    idle = _prepare_surface(raw_idle)
    walks = [_prepare_surface(w) for w in raw_walks]
    att = (
        _prepare_surface(raw_attack)
        if raw_attack is not None
        else _prepare_surface(build_player_attack_pose())
    )
    back = (
        _prepare_surface(raw_back)
        if raw_back is not None
        else _prepare_surface(build_player_back_view())
    )
    return idle, walks, att, back
