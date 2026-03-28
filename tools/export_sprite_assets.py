#!/usr/bin/env python3
"""
Exporta sprites procedimentais 64×64 para assets/sprites/<pasta>/.
Executar na raiz do projeto: python tools/export_sprite_assets.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pygame  # noqa: E402

from ui.procedural_sprites import (  # noqa: E402
    build_enemy_surface,
    build_player_attack_pose,
    build_player_back_view,
    build_player_idle,
    build_player_walk_frame,
)


def _save(surf: pygame.Surface, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surf, str(path))
    print("gravado", path.relative_to(_ROOT))


def main() -> None:
    pygame.init()

    enemy_map = {
        "corrupted_priest": "priest",
        "fallen_angel": "fallen_angel",
        "living_statue": "statue",
        "shadow_creature": "shadow",
    }
    for folder, kind in enemy_map.items():
        base = _ROOT / "assets" / "sprites" / folder
        s = build_enemy_surface(kind)
        for name in ("sprite.png", "idle.png", "walk.png", "attack.png"):
            _save(s, base / name)

    pdir = _ROOT / "assets" / "sprites" / "player"
    idle = build_player_idle()
    w1 = build_player_walk_frame(-1.0)
    w2 = build_player_walk_frame(1.0)
    _save(idle, pdir / "sprite.png")
    _save(idle, pdir / "idle.png")
    _save(w1, pdir / "walk.png")
    _save(w2, pdir / "walk_2.png")
    _save(idle, pdir / "attack.png")

    spr_root = _ROOT / "assets" / "sprites"
    _save(build_player_attack_pose(), spr_root / "player_attack.png")
    _save(build_player_back_view(), spr_root / "player_back.png")

    pygame.quit()
    print("Concluído.")


if __name__ == "__main__":
    main()
