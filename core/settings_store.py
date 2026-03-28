"""
Definições persistidas (resolução, ecrã completo, volume).
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_settings.json")

RESOLUTION_PRESETS: Tuple[Tuple[int, int], ...] = (
    (1280, 720),
    (1600, 900),
    (1920, 1080),
    (2560, 1440),
)


@dataclass
class Settings:
    window_width: int = 1920
    window_height: int = 1080
    fullscreen: bool = True
    master_volume: float = 0.75

    def clamp_volume(self) -> None:
        self.master_volume = max(0.0, min(1.0, float(self.master_volume)))


def default_settings() -> Settings:
    s = Settings()
    s.clamp_volume()
    return s


def load_settings(path: str = DEFAULT_PATH) -> Settings:
    if not os.path.isfile(path):
        return default_settings()
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw: Dict[str, Any] = json.load(f)
        s = Settings(
            window_width=int(raw.get("window_width", 1920)),
            window_height=int(raw.get("window_height", 1080)),
            fullscreen=bool(raw.get("fullscreen", True)),
            master_volume=float(raw.get("master_volume", 0.75)),
        )
        s.clamp_volume()
        return s
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return default_settings()


def save_settings(settings: Settings, path: str = DEFAULT_PATH) -> None:
    settings.clamp_volume()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(settings), f, indent=2)
    except OSError:
        pass
