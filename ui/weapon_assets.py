"""
Sprites de armas em assets/sprites/weapons/<sprite_key>.png
Escala ~36px altura; fallback procedural + log WARNING.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pygame

from core import game_logging

_log = game_logging.get_logger("sprites")

_ROOT = Path(__file__).resolve().parent.parent
_WEAPONS_DIR = _ROOT / "assets" / "sprites" / "weapons"

_CACHE: Dict[str, pygame.Surface] = {}
_TARGET_HEIGHT = 36


def clear_weapon_sprite_cache() -> None:
    _CACHE.clear()


def _placeholder(sprite_key: str) -> pygame.Surface:
    s = pygame.Surface((40, 40), pygame.SRCALPHA)
    hue = (hash(sprite_key) % 200) + 40
    pygame.draw.rect(s, (hue, hue // 2, hue // 3), (6, 10, 28, 24), border_radius=4)
    pygame.draw.rect(s, (200, 180, 120), (6, 10, 28, 24), 2, border_radius=4)
    return s


def get_weapon_surface(sprite_key: str) -> pygame.Surface:
    if sprite_key in _CACHE:
        return _CACHE[sprite_key]

    path = _WEAPONS_DIR / f"{sprite_key}.png"
    surf: pygame.Surface | None = None
    if path.is_file():
        try:
            surf = pygame.image.load(str(path))
            if pygame.display.get_init() and pygame.display.get_surface() is not None:
                surf = surf.convert_alpha()
        except (pygame.error, OSError) as e:
            _log.warning("Erro ao ler arma %s: %s", path.name, e)
            surf = None
    if surf is None:
        _log.warning("Sprite de arma em falta: %s — placeholder", path.name)
        surf = _placeholder(sprite_key)

    h = surf.get_height()
    if h > 0 and h != _TARGET_HEIGHT:
        scale = _TARGET_HEIGHT / h
        nw = max(1, int(surf.get_width() * scale))
        nh = max(1, int(h * scale))
        try:
            surf = pygame.transform.smoothscale(surf, (nw, nh))
        except (pygame.error, ValueError):
            surf = pygame.transform.scale(surf, (nw, nh))

    _CACHE[sprite_key] = surf
    return surf
