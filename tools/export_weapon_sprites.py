#!/usr/bin/env python3
"""Gera PNG 48×48 simples em assets/sprites/weapons/. Executar na raiz do projeto."""

from __future__ import annotations

import math
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

import pygame  # noqa: E402


def staff(surf: pygame.Surface) -> None:
    pygame.draw.rect(surf, (35, 28, 55), (20, 6, 8, 36), border_radius=2)
    pygame.draw.circle(surf, (180, 160, 255), (24, 10), 7)
    pygame.draw.circle(surf, (255, 240, 200), (24, 10), 3)


def sword(surf: pygame.Surface) -> None:
    pygame.draw.polygon(surf, (200, 200, 220), [(28, 8), (38, 28), (34, 30), (24, 12)])
    pygame.draw.polygon(surf, (90, 85, 110), [(28, 8), (38, 28), (34, 30), (24, 12)], 2)
    pygame.draw.rect(surf, (120, 90, 60), (22, 26, 8, 14), border_radius=2)


def whip(surf: pygame.Surface) -> None:
    pts = [(8, 36), (18, 28), (28, 32), (40, 14), (42, 16), (30, 36), (16, 38)]
    pygame.draw.lines(surf, (60, 45, 40), False, pts, 4)
    pygame.draw.circle(surf, (140, 50, 50), (42, 14), 5)


def holy_water(surf: pygame.Surface) -> None:
    pygame.draw.ellipse(surf, (80, 140, 220), (14, 10, 20, 30))
    pygame.draw.ellipse(surf, (180, 230, 255), (14, 10, 20, 30), 2)
    pygame.draw.rect(surf, (200, 200, 220), (20, 6, 8, 8), border_radius=2)


def tome(surf: pygame.Surface) -> None:
    pygame.draw.rect(surf, (45, 32, 52), (10, 12, 28, 28), border_radius=3)
    pygame.draw.rect(surf, (140, 100, 80), (10, 12, 28, 28), 2, border_radius=3)
    pygame.draw.line(surf, (200, 180, 140), (14, 20), (34, 20), 1)


def orb(surf: pygame.Surface) -> None:
    pygame.draw.circle(surf, (255, 230, 160), (24, 24), 14)
    pygame.draw.circle(surf, (255, 255, 220), (24, 24), 8)
    for i in range(6):
        a = i * math.pi / 3
        x, y = 24 + math.cos(a) * 10, 24 + math.sin(a) * 10
        pygame.draw.circle(surf, (255, 200, 120), (int(x), int(y)), 2)


def main() -> None:
    pygame.init()
    out_dir = _ROOT / "assets" / "sprites" / "weapons"
    out_dir.mkdir(parents=True, exist_ok=True)
    pairs = (
        ("staff.png", staff),
        ("sword.png", sword),
        ("whip.png", whip),
        ("holy_water.png", holy_water),
        ("tome.png", tome),
        ("orb.png", orb),
    )
    for name, fn in pairs:
        s = pygame.Surface((48, 48), pygame.SRCALPHA)
        fn(s)
        path = out_dir / name
        pygame.image.save(s, str(path))
        print("gravado", path.relative_to(_ROOT))
    pygame.quit()
    print("Concluído.")


if __name__ == "__main__":
    main()
