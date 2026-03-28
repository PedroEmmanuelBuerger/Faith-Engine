"""
Colisão do jogador com obstáculos sólidos do mundo (círculo vs círculo).
"""

from __future__ import annotations

import math
from typing import List

from entities.player import Player
from world.chunk_world import ChunkWorld


def _gather_solids(world: ChunkWorld, px: float, py: float, chunk_radius: int = 3) -> List[dict]:
    out: List[dict] = []
    pcx, pcy = world.world_to_chunk(px, py)
    for dcx in range(-chunk_radius, chunk_radius + 1):
        for dcy in range(-chunk_radius, chunk_radius + 1):
            for item in world.solids_for_chunk(pcx + dcx, pcy + dcy):
                out.append(item)
    return out


def resolve_player_vs_solids(player: Player, world: ChunkWorld, passes: int = 4) -> None:
    px, py = player.x, player.y
    pr = float(player.radius)
    solids = _gather_solids(world, px, py)
    for _ in range(passes):
        moved = False
        for o in solids:
            ox, oy = float(o["x"]), float(o["y"])
            cr = float(o["radius"])
            dx, dy = px - ox, py - oy
            dist = math.hypot(dx, dy)
            min_d = pr + cr
            if dist >= min_d or dist < 1e-9:
                continue
            if dist < 1e-6:
                px += min_d * 0.02
                py += 0.0
            else:
                push = (min_d - dist) / dist * 1.02
                px += dx * push
                py += dy * push
            moved = True
        if not moved:
            break
    player.x, player.y = px, py
