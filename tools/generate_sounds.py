"""
Gera WAV mínimos em assets/sounds/ (executar uma vez: python tools/generate_sounds.py).
"""

from __future__ import annotations

import math
import os
import struct
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "sounds")


def _write_wav(path: str, samples: list[int], framerate: int = 22050) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        for s in samples:
            w.writeframes(struct.pack("<h", max(-32767, min(32767, int(s)))))


def tone(freq: float, duration: float, fr: int, vol: float, fade: bool = True) -> list[int]:
    n = int(fr * duration)
    out: list[int] = []
    for i in range(n):
        t = i / fr
        env = 1.0
        if fade:
            env = min(1.0, i / max(1, int(fr * 0.02))) * min(
                1.0, (n - i) / max(1, int(fr * 0.05))
            )
        s = 32767 * vol * env * math.sin(2 * math.pi * freq * t)
        out.append(s)
    return out


def noise_burst(duration: float, fr: int, vol: float) -> list[int]:
    import random

    n = int(fr * duration)
    return [32767 * vol * (random.random() * 2 - 1) for _ in range(n)]


def main() -> None:
    shoot = tone(880, 0.06, 22050, 0.22) + tone(440, 0.04, 22050, 0.15)
    _write_wav(os.path.join(OUT, "shoot.wav"), shoot)

    hit = tone(200, 0.03, 22050, 0.35) + tone(120, 0.05, 22050, 0.25)
    _write_wav(os.path.join(OUT, "hit.wav"), hit)

    death = tone(150, 0.12, 22050, 0.4) + noise_burst(0.2, 22050, 0.08)
    _write_wav(os.path.join(OUT, "death.wav"), death)

    fr = 22050
    bgm: list[int] = []
    for _ in range(3):
        for note in (196, 220, 247, 262):
            bgm.extend(tone(note, 0.35, fr, 0.06, True))
    _write_wav(os.path.join(OUT, "bgm_loop.wav"), bgm, fr)
    print("Escrito em", OUT)


if __name__ == "__main__":
    main()
