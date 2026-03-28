"""
Áudio com pygame.mixer; volume mestre das definições.
Inicialização tolerante a falhas (sem dispositivo de áudio, etc.).
"""

from __future__ import annotations

import os
from typing import Dict, Optional

import pygame

from core import game_logging

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")
_log = game_logging.get_logger("audio")


class AudioManager:
    def __init__(self) -> None:
        self._master = 0.75
        self._music_path: Optional[str] = None
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._mixer_ok = False

    def init_mixer(self) -> None:
        self._mixer_ok = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            try:
                pygame.mixer.set_num_channels(16)
            except (pygame.error, AttributeError):
                pass
            self._mixer_ok = bool(pygame.mixer.get_init())
        except (pygame.error, RuntimeError, OSError) as e:
            _log.warning("Mixer init failed: %s — audio disabled", e)
            self._mixer_ok = False
        if self._mixer_ok:
            _log.info("pygame.mixer initialized")

    def set_master_volume(self, v: float) -> None:
        try:
            self._master = max(0.0, min(1.0, float(v)))
        except (TypeError, ValueError):
            self._master = 0.75
            _log.warning("Invalid volume value; using default 0.75")
        if not self._mixer_ok:
            return
        try:
            pygame.mixer.music.set_volume(self._master * 0.45)
        except (pygame.error, RuntimeError):
            pass
        for snd in self._sounds.values():
            try:
                snd.set_volume(self._master)
            except (pygame.error, RuntimeError):
                pass

    def load_all(self) -> None:
        self._sounds.clear()
        if not self._mixer_ok:
            _log.warning("Skipping sound load: mixer unavailable")
            return
        mapping = {
            "shoot": "shoot.wav",
            "hit": "hit.wav",
            "death": "death.wav",
            "pickup": "pickup.wav",
            "enemy_death": "enemy_death.wav",
            "shoot_heavy": "shoot_heavy.wav",
        }
        for key, fname in mapping.items():
            path = os.path.join(_ASSETS, fname)
            if not os.path.isfile(path):
                _log.warning("Missing sound asset: %s", fname)
                continue
            try:
                self._sounds[key] = pygame.mixer.Sound(path)
                self._sounds[key].set_volume(self._master)
            except (pygame.error, OSError, RuntimeError) as e:
                _log.warning("Could not load %s: %s", fname, e)
        self._music_path = os.path.join(_ASSETS, "bgm_loop.wav")
        if not os.path.isfile(self._music_path):
            self._music_path = None
            _log.warning("Missing bgm_loop.wav")

    def play_music_loop(self) -> None:
        if not self._mixer_ok or not self._music_path:
            return
        try:
            pygame.mixer.music.load(self._music_path)
            pygame.mixer.music.set_volume(self._master * 0.45)
            pygame.mixer.music.play(-1)
        except (pygame.error, OSError, RuntimeError) as e:
            _log.warning("Music playback failed: %s", e)

    def stop_music(self) -> None:
        if not self._mixer_ok:
            return
        try:
            pygame.mixer.music.stop()
        except (pygame.error, RuntimeError):
            pass

    def play_shoot(self) -> None:
        self._play("shoot", 0.55)

    def play_hit(self) -> None:
        self._play("hit", 0.7)

    def play_death(self) -> None:
        self._play("death", 0.85)

    def play_pickup(self) -> None:
        self._play("pickup", 0.62)

    def play_enemy_death(self) -> None:
        self._play("enemy_death", 0.58)

    def play_shoot_heavy(self) -> None:
        self._play("shoot_heavy", 0.62)

    def set_intensity_volume(self, intensity: float) -> None:
        """0 = calmo, 1 = caótico — mistura com volume mestre na música."""
        if not self._mixer_ok or not self._music_path:
            return
        t = max(0.0, min(1.0, float(intensity)))
        try:
            music_vol = self._master * (0.36 + t * 0.26)
            pygame.mixer.music.set_volume(music_vol)
        except (pygame.error, RuntimeError):
            pass

    def _play(self, name: str, rel: float) -> None:
        if not self._mixer_ok:
            return
        snd = self._sounds.get(name)
        if not snd:
            return
        try:
            snd.set_volume(self._master * rel)
            snd.play()
        except (pygame.error, RuntimeError):
            pass
