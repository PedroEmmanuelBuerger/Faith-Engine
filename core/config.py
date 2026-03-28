"""
Constantes globais: viewport (runtime), mundo, tema gótico.
"""

from __future__ import annotations

# Janela — atualizado em runtime por display.apply_video_mode
VIEWPORT_W = 1280
VIEWPORT_H = 720
FPS = 60

# Mundo infinito (sem bordas fixas; mantidos para compat legada se necessário)
WORLD_W = 10_000_000.0
WORLD_H = 10_000_000.0

TILE_SIZE = 48
PROJECTILE_MAX_DIST_FROM_PLAYER = 640.0
MAX_ENEMIES_ALIVE = 140

GAME_TITLE = "Culto do Infinito"

# Paleta gótica / igreja
COLOR_VOID = (14, 10, 22)
COLOR_STONE_DARK = (38, 34, 52)
COLOR_STONE_MID = (52, 48, 68)
COLOR_STONE_LIGHT = (72, 66, 92)
COLOR_GOLD_DIM = (160, 140, 90)
COLOR_GOLD_BRIGHT = (220, 190, 120)
COLOR_BLOOD = (140, 40, 55)
COLOR_SHADOW = (25, 22, 38)
COLOR_EYE_GLOW = (180, 255, 220)
COLOR_PROJECTILE_CORE = (255, 240, 200)
COLOR_PROJECTILE_GLOW = (200, 160, 255)

PLAYER_SPRITE_HEIGHT = 75
PLAYER_WALK_FRAME_SEC = 0.14


def set_viewport(width: int, height: int) -> None:
    global VIEWPORT_W, VIEWPORT_H
    VIEWPORT_W = max(320, int(width))
    VIEWPORT_H = max(240, int(height))
