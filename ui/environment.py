"""
Arena gótica: chão em pedra, pilares, símbolos (procedural — trocável por tiles depois).
"""

from __future__ import annotations

import math

import pygame

from core import config


def draw_church_floor(
    surface: pygame.Surface, camera_x: float, camera_y: float
) -> None:
    """Ladrilhos com variação sutil de tom."""
    ts = config.TILE_SIZE
    gx0 = int(camera_x // ts) * ts
    gy0 = int(camera_y // ts) * ts
    for wx in range(gx0, int(camera_x + config.VIEWPORT_W) + ts * 2, ts):
        for wy in range(gy0, int(camera_y + config.VIEWPORT_H) + ts * 2, ts):
            if wx < 0 or wy < 0 or wx >= config.WORLD_W or wy >= config.WORLD_H:
                continue
            sx = int(wx - camera_x)
            sy = int(wy - camera_y)
            shade = ((wx // ts) + (wy // ts)) % 3
            if shade == 0:
                c = config.COLOR_STONE_DARK
            elif shade == 1:
                c = config.COLOR_STONE_MID
            else:
                c = config.COLOR_STONE_LIGHT
            r = pygame.Rect(sx, sy, ts - 1, ts - 1)
            pygame.draw.rect(surface, c, r)
            pygame.draw.rect(surface, (22, 18, 32), r, 1)


def draw_decorations(
    surface: pygame.Surface, camera_x: float, camera_y: float
) -> None:
    """Pilares e runas fixas no mundo."""
    pillars = [
        (420, 380),
        (820, 520),
        (1900, 720),
        (2200, 1200),
        (600, 1400),
        (1500, 300),
    ]
    for wx, wy in pillars:
        sx = int(wx - camera_x)
        sy = int(wy - camera_y)
        if sx < -80 or sy < -120 or sx > config.VIEWPORT_W + 80:
            continue
        base = pygame.Rect(sx - 22, sy - 90, 44, 100)
        pygame.draw.rect(surface, config.COLOR_STONE_MID, base, border_radius=4)
        pygame.draw.rect(surface, config.COLOR_GOLD_DIM, base, 2, border_radius=4)
        cap = pygame.Rect(sx - 28, sy - 100, 56, 18)
        pygame.draw.rect(surface, config.COLOR_STONE_LIGHT, cap, border_radius=3)

    # Círculos rúnicos
    for cx, cy, rad in [(1100, 900, 140), (700, 1100, 100), (2000, 400, 90)]:
        sx = int(cx - camera_x)
        sy = int(cy - camera_y)
        if sx < -rad or sy < -rad or sx > config.VIEWPORT_W + rad:
            continue
        pygame.draw.circle(
            surface, config.COLOR_GOLD_DIM, (sx, sy), rad, 2
        )
        for i in range(6):
            ang = i * math.pi / 3
            x2 = sx + math.cos(ang) * (rad - 10)
            y2 = sy + math.sin(ang) * (rad - 10)
            pygame.draw.line(surface, config.COLOR_GOLD_DIM, (sx, sy), (int(x2), int(y2)), 1)


def draw_world_background(
    surface: pygame.Surface, camera_x: float, camera_y: float
) -> None:
    surface.fill(config.COLOR_VOID)
    draw_church_floor(surface, camera_x, camera_y)
    draw_decorations(surface, camera_x, camera_y)
