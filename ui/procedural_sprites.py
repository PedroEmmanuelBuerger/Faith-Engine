"""
Sprites 64×64 gerados por código — estilo gótico / dark fantasy.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

import pygame

SIZE = 64
CX, CY = SIZE // 2, SIZE - 12


def _surface() -> pygame.Surface:
    s = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    return s


def _glow_circle(
    surf: pygame.Surface, pos: Tuple[int, int], r: int, core: Tuple[int, int, int, int]
) -> None:
    for i in range(3, 0, -1):
        a = max(20, core[3] // (4 - i))
        pygame.draw.circle(surf, (*core[:3], a), pos, r + i * 2)


def build_player_idle() -> pygame.Surface:
    s = _surface()
    # Manto
    pygame.draw.ellipse(s, (22, 18, 38), (12, 28, 40, 34))
    pygame.draw.ellipse(s, (38, 32, 58), (12, 28, 40, 34), 2)
    pygame.draw.rect(s, (30, 26, 48), (20, 38, 24, 22), border_radius=4)
    # Capuz
    pygame.draw.ellipse(s, (18, 14, 32), (14, 8, 36, 36))
    pygame.draw.arc(s, (55, 48, 78), (14, 8, 36, 36), math.pi * 0.15, math.pi * 0.85, 2)
    # Olhos brilhantes
    _glow_circle(s, (CX - 10, CY - 22), 3, (160, 255, 220, 200))
    _glow_circle(s, (CX + 10, CY - 22), 3, (160, 255, 220, 200))
    pygame.draw.circle(s, (220, 255, 240), (CX - 10, CY - 22), 2)
    pygame.draw.circle(s, (220, 255, 240), (CX + 10, CY - 22), 2)
    return s


def build_player_walk_frame(lean: float) -> pygame.Surface:
    s = _surface()
    off = int(lean * 4)
    pygame.draw.ellipse(s, (22, 18, 38), (10 + off, 26, 22, 36))
    pygame.draw.ellipse(s, (18, 14, 30), (8 + off, 10, 28, 30))
    pygame.draw.ellipse(s, (38, 32, 58), (8 + off, 10, 28, 30), 2)
    pygame.draw.rect(s, (28, 24, 45), (14 + off, 34, 14, 20), border_radius=3)
    eye_x = CX - 6 + off
    _glow_circle(s, (eye_x, CY - 20), 3, (150, 255, 210, 180))
    pygame.draw.circle(s, (230, 255, 245), (eye_x, CY - 20), 2)
    return s


def _enemy_corrupt_priest() -> pygame.Surface:
    s = _surface()
    pygame.draw.ellipse(s, (95, 28, 42), (16, 30, 32, 30))
    pygame.draw.rect(s, (55, 38, 52), (20, 38, 24, 20), border_radius=3)
    pygame.draw.circle(s, (210, 200, 215), (CX, CY - 18), 7)
    pygame.draw.circle(s, (255, 60, 70), (CX - 2, CY - 18), 2)
    pygame.draw.line(s, (70, 50, 60), (CX, CY - 10), (CX, CY + 2), 2)
    return s


def _enemy_fallen_angel() -> pygame.Surface:
    s = _surface()
    # Asas partidas
    pygame.draw.polygon(s, (45, 40, 62), [(4, 28), (22, 20), (18, 40)])
    pygame.draw.polygon(s, (45, 40, 62), [(60, 26), (44, 18), (48, 38)])
    pygame.draw.polygon(s, (35, 32, 55), [(4, 28), (22, 20), (18, 40)], 1)
    # Corpo
    pygame.draw.ellipse(s, (200, 195, 210), (22, 26, 20, 28))
    # Halo distorcido
    pygame.draw.arc(s, (120, 100, 140), (10, 4, 44, 24), 0.2, math.pi - 0.2, 2)
    pygame.draw.arc(s, (180, 60, 80), (12, 6, 40, 20), math.pi + 0.3, math.tau - 0.3, 2)
    pygame.draw.circle(s, (40, 35, 90), (CX - 5, CY - 14), 2)
    pygame.draw.circle(s, (40, 35, 90), (CX + 5, CY - 14), 2)
    return s


def _enemy_living_statue() -> pygame.Surface:
    s = _surface()
    body = pygame.Rect(14, 18, 36, 38)
    pygame.draw.rect(s, (88, 84, 102), body, border_radius=5)
    pygame.draw.rect(s, (120, 115, 138), body, 2, border_radius=5)
    pygame.draw.rect(s, (70, 66, 85), (22, 26, 20, 22), border_radius=3)
    pygame.draw.circle(s, (160, 150, 175), (CX, CY - 18), 8)
    for lx, ly in ((18, 30), (44, 34), (26, 48)):
        pygame.draw.line(s, (50, 48, 65), (lx, ly), (lx + 4, ly + 6), 1)
    pygame.draw.circle(s, (140, 130, 90), (CX, CY - 22), 5)
    return s


def _enemy_shadow() -> pygame.Surface:
    s = _surface()
    pygame.draw.ellipse(s, (28, 22, 48), (10, 28, 44, 28))
    pygame.draw.ellipse(s, (55, 40, 85), (10, 28, 44, 28), 2)
    pygame.draw.ellipse(s, (20, 16, 38), (16, 14, 32, 26))
    _glow_circle(s, (CX - 8, CY - 8), 3, (220, 70, 90, 160))
    _glow_circle(s, (CX + 8, CY - 8), 3, (220, 70, 90, 160))
    pygame.draw.circle(s, (255, 90, 110), (CX - 8, CY - 8), 2)
    pygame.draw.circle(s, (255, 90, 110), (CX + 8, CY - 8), 2)
    return s


def _enemy_skitter() -> pygame.Surface:
    s = _surface()
    pygame.draw.polygon(s, (120, 70, 140), [(CX, 12), (52, 48), (12, 48)])
    pygame.draw.polygon(s, (90, 50, 110), [(CX, 12), (52, 48), (12, 48)], 2)
    return s


def _enemy_bulwark() -> pygame.Surface:
    s = _surface()
    pygame.draw.rect(s, (52, 48, 68), (10, 14, 44, 42), border_radius=8)
    pygame.draw.rect(s, (95, 90, 115), (10, 14, 44, 42), 3, border_radius=8)
    pygame.draw.rect(s, (40, 38, 55), (22, 22, 20, 24), border_radius=4)
    return s


def _enemy_heretic() -> pygame.Surface:
    s = _surface()
    pygame.draw.rect(s, (115, 62, 58), (18, 20, 28, 36), border_radius=5)
    pygame.draw.line(s, (200, 200, 255), (46, CY - 6), (56, CY - 10), 2)
    pygame.draw.circle(s, (210, 190, 185), (CX, CY - 14), 6)
    return s


def _enemy_carrion() -> pygame.Surface:
    s = _surface()
    pygame.draw.circle(s, (65, 120, 55), (CX, CY), 22)
    pygame.draw.circle(s, (40, 85, 40), (CX, CY), 22, 2)
    pygame.draw.circle(s, (255, 220, 80), (CX, CY), 10)
    pygame.draw.circle(s, (255, 100, 60), (CX, CY), 4)
    return s


_ENEMY_BUILDERS = {
    "priest": _enemy_corrupt_priest,
    "statue": _enemy_living_statue,
    "shadow": _enemy_shadow,
    "fallen_angel": _enemy_fallen_angel,
    "skitter": _enemy_skitter,
    "bulwark": _enemy_bulwark,
    "heretic": _enemy_heretic,
    "carrion_bomb": _enemy_carrion,
}

_CACHE: Dict[str, pygame.Surface] = {}


def build_enemy_surface(kind: str) -> pygame.Surface:
    """Gera 64×64 procedural (sem cache de ficheiro). Usado em export e fallback."""
    bkey = kind if kind in _ENEMY_BUILDERS else "priest"
    return _ENEMY_BUILDERS[bkey]()


def enemy_sprite_for_kind(kind: str) -> pygame.Surface:
    if kind in _CACHE:
        return _CACHE[kind]
    surf = build_enemy_surface(kind)
    _CACHE[kind] = surf
    return surf


def load_procedural_player_sprites() -> Tuple[pygame.Surface, List[pygame.Surface]]:
    idle = build_player_idle()
    walk = [build_player_walk_frame(-1.0), build_player_walk_frame(1.0)]
    return idle, walk
