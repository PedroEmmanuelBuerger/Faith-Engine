"""
Mapa infinito em tiles: chunks 16×16, geração determinística por semente.
Obstáculos sólidos (pilares, estátuas, altares) com colisão para o jogador.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

import pygame

from core import config

CHUNK_TILES = 16


def _hash_u32(seed: int, *parts: int) -> int:
    h = (seed ^ 2166136261) & 0xFFFFFFFF
    for p in parts:
        h = (h ^ (int(p) & 0xFFFFFFFF)) * 16777619
        h &= 0xFFFFFFFF
    return h


class ChunkWorld:
    """Gera e desenha chão + decoração procedural; cache leve por chunk."""

    def __init__(self, seed: int) -> None:
        self.seed = seed & 0xFFFFFFFF
        self._deco_cache: Dict[Tuple[int, int], List[dict]] = {}

    def clear_caches(self) -> None:
        self._deco_cache.clear()

    def world_to_chunk(self, wx: float, wy: float) -> Tuple[int, int]:
        ts = config.TILE_SIZE * CHUNK_TILES
        return int(math.floor(wx / ts)), int(math.floor(wy / ts))

    def prune_caches(self, player_x: float, player_y: float, radius_chunks: int = 10) -> None:
        pcx, pcy = self.world_to_chunk(player_x, player_y)
        for key in list(self._deco_cache.keys()):
            cx, cy = key
            if abs(cx - pcx) > radius_chunks or abs(cy - pcy) > radius_chunks:
                del self._deco_cache[key]

    def solids_for_chunk(self, cx: int, cy: int) -> List[dict]:
        return [d for d in self._decor_for_chunk(cx, cy) if d.get("collide")]

    def _tile_variant(self, wtx: int, wty: int) -> int:
        h = _hash_u32(self.seed, wtx, wty, 0xC0FFEE)
        return h % 5

    def _tile_color(self, variant: int) -> Tuple[int, int, int]:
        if variant == 0:
            return config.COLOR_STONE_DARK
        if variant == 1:
            return config.COLOR_STONE_MID
        if variant == 2:
            return config.COLOR_STONE_LIGHT
        if variant == 3:
            return (44, 40, 58)
        return (62, 56, 78)

    def _decor_for_chunk(self, cx: int, cy: int) -> List[dict]:
        key = (cx, cy)
        if key in self._deco_cache:
            return self._deco_cache[key]
        ts = config.TILE_SIZE
        cw = CHUNK_TILES * ts
        base_x = cx * cw
        base_y = cy * cw
        h0 = _hash_u32(self.seed, cx, cy, 0xDEC0)
        items: List[dict] = []
        n_pill = h0 % 3
        for i in range(n_pill):
            h = _hash_u32(h0, i, 0x7111)
            lx = (h % (CHUNK_TILES - 4) + 2) * ts + ts // 2
            ly = ((h >> 8) % (CHUNK_TILES - 4) + 2) * ts + ts // 2
            items.append(
                {
                    "type": "pillar",
                    "x": base_x + lx,
                    "y": base_y + ly,
                    "collide": True,
                    "radius": 24.0,
                }
            )

        h_stat = _hash_u32(h0, 0xB717)
        if h_stat % 6 == 0:
            lx = (h_stat % (CHUNK_TILES - 6) + 3) * ts + ts // 2
            ly = ((h_stat >> 4) % (CHUNK_TILES - 6) + 3) * ts + ts // 2
            items.append(
                {
                    "type": "broken_statue",
                    "x": base_x + lx,
                    "y": base_y + ly,
                    "collide": True,
                    "radius": 20.0,
                }
            )

        h_alt = _hash_u32(h0, 0xA112)
        if h_alt % 11 == 2:
            ax = base_x + cw // 2 + ((h_alt >> 8) % 120 - 60)
            ay = base_y + cw // 2 + ((h_alt >> 16) % 120 - 60)
            items.append(
                {
                    "type": "altar",
                    "x": ax,
                    "y": ay,
                    "collide": True,
                    "radius": 30.0,
                }
            )

        if _hash_u32(h0, 0x5275) % 4 == 0:
            rx = base_x + cw // 2
            ry = base_y + cw // 2
            rad = 40 + (h0 % 50)
            items.append(
                {
                    "type": "rune",
                    "x": rx,
                    "y": ry,
                    "r": float(rad),
                    "collide": False,
                }
            )
        self._deco_cache[key] = items
        return items

    def draw(
        self,
        surface: pygame.Surface,
        camera_x: float,
        camera_y: float,
    ) -> None:
        vw, vh = config.VIEWPORT_W, config.VIEWPORT_H
        ts = config.TILE_SIZE
        surface.fill(config.COLOR_VOID)

        t0x = int(math.floor(camera_x / ts))
        t0y = int(math.floor(camera_y / ts))
        t1x = int(math.ceil((camera_x + vw) / ts)) + 1
        t1y = int(math.ceil((camera_y + vh) / ts)) + 1

        for ty in range(t0y, t1y):
            for tx in range(t0x, t1x):
                wx = tx * ts
                wy = ty * ts
                sx = int(wx - camera_x)
                sy = int(wy - camera_y)
                v = self._tile_variant(tx, ty)
                c = self._tile_color(v)
                r = pygame.Rect(sx, sy, ts - 1, ts - 1)
                pygame.draw.rect(surface, c, r)
                edge = (22, 18, 32)
                if self._tile_variant(tx + 1, ty) != v:
                    pygame.draw.line(surface, edge, (sx + ts - 1, sy), (sx + ts - 1, sy + ts), 1)
                if self._tile_variant(tx, ty + 1) != v:
                    pygame.draw.line(surface, edge, (sx, sy + ts - 1), (sx + ts, sy + ts - 1), 1)

        ccx0 = int(math.floor(camera_x / (CHUNK_TILES * ts)))
        ccy0 = int(math.floor(camera_y / (CHUNK_TILES * ts)))
        ccx1 = int(math.ceil((camera_x + vw) / (CHUNK_TILES * ts)))
        ccy1 = int(math.ceil((camera_y + vh) / (CHUNK_TILES * ts)))

        for ccy in range(ccy0 - 1, ccy1 + 1):
            for ccx in range(ccx0 - 1, ccx1 + 1):
                for d in self._decor_for_chunk(ccx, ccy):
                    wx, wy = d["x"], d["y"]
                    sx = int(wx - camera_x)
                    sy = int(wy - camera_y)
                    if sx < -160 or sy < -160 or sx > vw + 160 or sy > vh + 160:
                        continue
                    typ = d["type"]
                    if typ == "pillar":
                        base = pygame.Rect(sx - 22, sy - 90, 44, 100)
                        pygame.draw.rect(surface, config.COLOR_STONE_MID, base, border_radius=4)
                        pygame.draw.rect(surface, config.COLOR_GOLD_DIM, base, 2, border_radius=4)
                        cap = pygame.Rect(sx - 28, sy - 100, 56, 18)
                        pygame.draw.rect(surface, config.COLOR_STONE_LIGHT, cap, border_radius=3)
                    elif typ == "broken_statue":
                        stump = pygame.Rect(sx - 18, sy - 52, 36, 56)
                        pygame.draw.rect(surface, (72, 68, 88), stump, border_radius=4)
                        pygame.draw.rect(surface, (110, 105, 125), stump, 2, border_radius=4)
                        pygame.draw.polygon(
                            surface,
                            (60, 58, 78),
                            [(sx - 14, sy - 50), (sx + 4, sy - 78), (sx + 18, sy - 48)],
                        )
                        pygame.draw.line(surface, (45, 42, 58), (sx - 6, sy - 30), (sx + 10, sy - 20), 2)
                    elif typ == "altar":
                        top = pygame.Rect(sx - 38, sy - 28, 76, 22)
                        pygame.draw.rect(surface, (48, 42, 62), top, border_radius=3)
                        pygame.draw.rect(surface, (95, 80, 55), top, 2, border_radius=3)
                        pygame.draw.rect(surface, (38, 32, 52), (sx - 30, sy - 8, 60, 14))
                        pygame.draw.ellipse(surface, (90, 35, 45), (sx - 8, sy - 36, 16, 10))
                    else:
                        rad = int(d["r"])
                        pygame.draw.circle(surface, config.COLOR_GOLD_DIM, (sx, sy), rad, 2)
                        for i in range(6):
                            ang = i * math.pi / 3
                            x2 = sx + math.cos(ang) * (rad - 10)
                            y2 = sy + math.sin(ang) * (rad - 10)
                            pygame.draw.line(
                                surface, config.COLOR_GOLD_DIM, (sx, sy), (int(x2), int(y2)), 1
                            )
