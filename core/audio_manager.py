"""
Áudio com pygame.mixer; volume mestre das definições.
"""

from __future__ import annotations

import os
from typing import Dict, Optional

import pygame

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")


class AudioManager:
    def __init__(self) -> None:
        self._master = 0.75
        self._music_path: Optional[str] = None
        self._sounds: Dict[str, pygame.mixer.Sound] = {}

    def init_mixer(self) -> None:
        pygame.mixer.init()
        try:
            pygame.mixer.set_num_channels(16)
        except pygame.error:
            pass

    def set_master_volume(self, v: float) -> None:
        self._master = max(0.0, min(1.0, float(v)))
        try:
            pygame.mixer.music.set_volume(self._master * 0.45)
        except pygame.error:
            pass
        for snd in self._sounds.values():
            try:
                snd.set_volume(self._master)
            except pygame.error:
                pass

    def load_all(self) -> None:
        self._sounds.clear()
        mapping = {
            "shoot": "shoot.wav",
            "hit": "hit.wav",
            "death": "death.wav",
        }
        for key, fname in mapping.items():
            path = os.path.join(_ASSETS, fname)
            if os.path.isfile(path):
                try:
                    self._sounds[key] = pygame.mixer.Sound(path)
                    self._sounds[key].set_volume(self._master)
                except pygame.error:
                    pass
        self._music_path = os.path.join(_ASSETS, "bgm_loop.wav")
        if not os.path.isfile(self._music_path):
            self._music_path = None

    def play_music_loop(self) -> None:
        if not self._music_path:
            return
        try:
            pygame.mixer.music.load(self._music_path)
            pygame.mixer.music.set_volume(self._master * 0.45)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def stop_music(self) -> None:
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass

    def play_shoot(self) -> None:
        self._play("shoot", 0.55)

    def play_hit(self) -> None:
        self._play("hit", 0.7)

    def play_death(self) -> None:
        self._play("death", 0.85)

    def _play(self, name: str, rel: float) -> None:
        snd = self._sounds.get(name)
        if not snd:
            return
        try:
            snd.set_volume(self._master * rel)
            snd.play()
        except pygame.error:
            pass
