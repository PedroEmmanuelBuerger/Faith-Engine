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
    "charger": "skitter",
    "splitter": "shadow_creature",
    "hierophant": "fallen_angel",
}

PLAYER_DIR = "player"

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


def _first_existing(paths: List[Path]) -> Optional[pygame.Surface]:
    for p in paths:
        surf = _load_png(p)
        if surf is not None:
            return surf
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
    from ui import procedural_sprites

    procedural_sprites.clear_runtime_enemy_cache()


def load_player_sprites_dynamic() -> Tuple[
    Optional[pygame.Surface],
    Optional[List[pygame.Surface]],
]:
    """
    Prioridade: raiz assets/sprites/ → assets/sprites/player/
    Nomes: player_idle.png, player_walk.png, player_walk_2.png (ou idle/walk na pasta player/).
    """
    pdir = _SPRITES / PLAYER_DIR

    idle = _first_existing(
        [
            _SPRITES / "player_idle.png",
            pdir / "player_idle.png",
            pdir / "idle.png",
            pdir / "sprite.png",
        ]
    )

    walk1 = _first_existing(
        [
            _SPRITES / "player_walk.png",
            pdir / "player_walk.png",
            pdir / "walk.png",
            pdir / "walk_1.png",
        ]
    )

    if idle is None or walk1 is None:
        if idle is None and walk1 is None:
            _log.warning(
                "Sprites do jogador em falta (player_idle.png / player_walk.png na raiz ou player/)"
            )
        else:
            _log.warning("Sprites do jogador incompletos (falta idle ou walk)")
        return None, None

    walk2 = _first_existing(
        [
            _SPRITES / "player_walk_2.png",
            pdir / "player_walk_2.png",
            pdir / "walk_2.png",
            pdir / "walk_alt.png",
        ]
    )
    w2 = walk2 if walk2 is not None else walk1
    walks: List[pygame.Surface] = [walk1, w2]

    return idle, walks
