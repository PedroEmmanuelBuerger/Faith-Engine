"""
Fontes góticas: Cinzel (UI principal) e UnifrakturCook (títulos especiais).
Coloca os .ttf em assets/fonts/ — ver assets/fonts/FONTS.txt
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pygame

from core import game_logging

_log = game_logging.get_logger("fonts")

_ROOT = Path(__file__).resolve().parent.parent
_FONTS_DIR = _ROOT / "assets" / "fonts"


def _first_existing(candidates: Iterable[str]) -> Optional[Path]:
    for name in candidates:
        p = _FONTS_DIR / name
        if p.is_file():
            return p
    return None


def _load_ttf(size: int, candidates: tuple[str, ...], bold: bool = False) -> Optional[pygame.font.Font]:
    path = _first_existing(candidates)
    if path is None:
        return None
    try:
        return pygame.font.Font(str(path), size)
    except (OSError, pygame.error) as e:
        _log.warning("Falha ao carregar fonte %s: %s", path.name, e)
        return None


def _sys_fallback(
    size: int, names: tuple[str, ...], bold: bool = False
) -> pygame.font.Font:
    for n in names:
        try:
            f = pygame.font.SysFont(n, size, bold=bold)
            if f:
                return f
        except (OSError, pygame.error):
            continue
    return pygame.font.SysFont(None, size, bold=bold)


@dataclass
class GameFonts:
    """Hierarquia: grande títulos, médio botões/cartas, pequeno stats."""

    title_large: pygame.font.Font
    title_medium: pygame.font.Font
    body: pygame.font.Font
    small: pygame.font.Font
    gothic_title: pygame.font.Font


def load_game_fonts() -> GameFonts:
    """Carrega Cinzel / fallbacks; UnifrakturCook para game over se existir."""
    cinzel_candidates = (
        "Cinzel-Bold.ttf",
        "Cinzel-SemiBold.ttf",
        "Cinzel-Regular.ttf",
        "Cinzel.ttf",
    )
    uni_candidates = (
        "UnifrakturCook-Bold.ttf",
        "UnifrakturCook.ttf",
        "UnifrakturMaguntia.ttf",
    )

    title_large = _load_ttf(44, cinzel_candidates, bold=True) or _sys_fallback(
        44, ("cinzel", "times new roman", "georgia"), bold=True
    )
    title_medium = _load_ttf(30, cinzel_candidates, bold=True) or _sys_fallback(
        30, ("cinzel", "times new roman"), bold=True
    )
    body = _load_ttf(22, ("Cinzel-Regular.ttf", "Cinzel-Medium.ttf", "Cinzel.ttf")) or _sys_fallback(
        22, ("cinzel", "times new roman"), bold=False
    )
    small = _load_ttf(16, ("Cinzel-Regular.ttf", "Cinzel.ttf")) or _sys_fallback(
        16, ("cinzel", "segoe ui"), bold=False
    )
    gothic = _load_ttf(52, uni_candidates, bold=True) or _load_ttf(
        52, cinzel_candidates, bold=True
    ) or _sys_fallback(52, ("unifrakturcook", "old english text mt", "times new roman"), bold=True)

    if _first_existing(cinzel_candidates):
        _log.info("Fonte Cinzel carregada de assets/fonts/")
    else:
        _log.warning("Cinzel não encontrada em assets/fonts/ — a usar fonte do sistema")

    return GameFonts(
        title_large=title_large,
        title_medium=title_medium,
        body=body,
        small=small,
        gothic_title=gothic,
    )
