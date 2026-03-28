"""
Carregamento dinâmico de sprites em assets/sprites/<pasta>/.
Fallback para geração procedural + log WARNING.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from core import game_logging

_log = game_logging.get_logger("sprites")

_ROOT = Path(__file__).resolve().parent.parent
_SPRITES = _ROOT / "assets" / "sprites"

# kind (EnemyKind value) → pasta sob assets/sprites/
ENEMY_KIND_TO_FOLDER: Dict[str, str] = {
    "priest": "corrupted_priest",
    "fallen_angel": "fallen_angel",
    "statue": "living_statue",
    "shadow": "shadow_creature",
    "skitter": "shadow_creature",
    "bulwark": "living_statue",
    "heretic": "corrupted_priest",
    "carrion_bomb": "corrupted_priest",
}

PLAYER_DIR = "player"

# Ordem de preferência por animação
PLAYER_IDLE_NAMES = ("idle.png", "sprite.png")
PLAYER_WALK_NAMES = ("walk.png", "walk_1.png")
PLAYER_WALK2_NAMES = ("walk_2.png", "walk_alt.png")

# Legacy paths (raiz de sprites/)
_LEGACY_IDLE = _SPRITES / "player_idle.png"
_LEGACY_WALK = _SPRITES / "player_walk.png"
_LEGACY_WALK2 = _SPRITES / "player_walk_2.png"

_ENEMY_CACHE: Dict[str, pygame.Surface] = {}


def sprites_root() -> Path:
    return _SPRITES


def _load_png(path: Path) -> Optional[pygame.Surface]:
    if not path.is_file():
        return None
    try:
        s = pygame.image.load(str(path))
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            s = s.convert_alpha()
        return s
    except (pygame.error, OSError) as e:
        _log.warning("Erro ao ler sprite %s: %s", path, e)
        return None


def enemy_folder_for_kind(kind: str) -> str:
    return ENEMY_KIND_TO_FOLDER.get(kind, "corrupted_priest")


def load_enemy_sprite(kind: str) -> pygame.Surface:
    """64×64 esperado; escala na UI se necessário."""
    if kind in _ENEMY_CACHE:
        return _ENEMY_CACHE[kind]

    folder = enemy_folder_for_kind(kind)
    for name in ("sprite.png", "idle.png"):
        path = _SPRITES / folder / name
        surf = _load_png(path)
        if surf is not None:
            _log.debug("Sprite inimigo carregado: %s/%s", folder, name)
            _ENEMY_CACHE[kind] = surf
            return surf

    _log.warning(
        "Sprite em falta para inimigo '%s' (pasta %s) — placeholder procedural",
        kind,
        folder,
    )
    from ui import procedural_sprites

    surf = procedural_sprites.build_enemy_surface(kind)
    _ENEMY_CACHE[kind] = surf
    return surf


def clear_enemy_sprite_cache() -> None:
    _ENEMY_CACHE.clear()


def load_player_sprites_dynamic() -> Tuple[
    Optional[pygame.Surface], Optional[List[pygame.Surface]]
]:
    """
    Ordem: assets/sprites/player/ → legacy na raiz → None (caller usa procedural).
    """
    pdir = _SPRITES / PLAYER_DIR
    idle_s: Optional[pygame.Surface] = None
    for n in PLAYER_IDLE_NAMES:
        idle_s = _load_png(pdir / n)
        if idle_s is not None:
            break
    if idle_s is None:
        idle_s = _load_png(_LEGACY_IDLE)

    walk1: Optional[pygame.Surface] = None
    for n in PLAYER_WALK_NAMES:
        walk1 = _load_png(pdir / n)
        if walk1 is not None:
            break
    if walk1 is None:
        walk1 = _load_png(_LEGACY_WALK)

    if idle_s is None or walk1 is None:
        if idle_s is None and walk1 is None:
            _log.warning(
                "Sprites do jogador em falta em assets/sprites/player/ — placeholder procedural"
            )
        else:
            _log.warning("Sprites do jogador incompletos — placeholder procedural")
        return None, None

    walk2: Optional[pygame.Surface] = None
    for n in PLAYER_WALK2_NAMES:
        walk2 = _load_png(pdir / n)
        if walk2 is not None:
            break
    if walk2 is None:
        walk2 = _load_png(_LEGACY_WALK2)
    walks: List[pygame.Surface] = [walk1, walk2 if walk2 is not None else walk1]
    return idle_s, walks
