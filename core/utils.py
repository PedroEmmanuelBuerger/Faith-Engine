"""Funções geométricas e conversão mundo ↔ ecrã."""


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def world_to_screen(
    wx: float, wy: float, camera_x: float, camera_y: float
) -> tuple[float, float]:
    return wx - camera_x, wy - camera_y


def screen_to_world(
    sx: float, sy: float, camera_x: float, camera_y: float
) -> tuple[float, float]:
    return sx + camera_x, sy + camera_y


def point_in_rect(px: float, py: float, rect: tuple[float, float, float, float]) -> bool:
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h
