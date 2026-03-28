"""
Menu principal: tema gótico e partículas subtis de fundo.
"""

from __future__ import annotations

import math
import random
from typing import List, Optional, Tuple

import pygame

from core import config
from ui.font_loader import GameFonts


class MainMenuScene:
    def __init__(self, vw: int, vh: int, fonts: GameFonts) -> None:
        self.vw = vw
        self.vh = vh
        self._fonts = fonts
        self.title_font = fonts.title_large
        self.menu_font = fonts.body
        self.sub_font = fonts.small
        self._particles: List[dict] = []
        self._spawn_t = 0.0
        self._btn_start: Optional[pygame.Rect] = None
        self._btn_settings: Optional[pygame.Rect] = None
        self._btn_exit: Optional[pygame.Rect] = None
        self._hover = -1

    def on_resize(self, vw: int, vh: int) -> None:
        self.vw = vw
        self.vh = vh

    def _layout(self) -> Tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
        cx, cy = self.vw // 2, self.vh // 2 + 40
        bw, bh, gap = 280, 48, 14
        r0 = pygame.Rect(cx - bw // 2, cy, bw, bh)
        r1 = pygame.Rect(cx - bw // 2, cy + bh + gap, bw, bh)
        r2 = pygame.Rect(cx - bw // 2, cy + (bh + gap) * 2, bw, bh)
        return r0, r1, r2

    def update(self, dt: float) -> None:
        self._spawn_t += dt
        if self._spawn_t > 0.08:
            self._spawn_t = 0.0
            self._particles.append(
                {
                    "x": random.uniform(0, self.vw),
                    "y": self.vh + 10,
                    "vy": random.uniform(-40, -90),
                    "vx": random.uniform(-14, 14),
                    "life": random.uniform(2.5, 4.5),
                    "r": random.uniform(1.5, 3.5),
                    "c": random.choice(
                        ((90, 80, 120), (120, 100, 160), (60, 50, 90), (140, 120, 180))
                    ),
                }
            )
        alive = []
        for p in self._particles:
            p["life"] -= dt
            if p["life"] <= 0:
                continue
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            alive.append(p)
        self._particles = alive

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(config.COLOR_VOID)
        for p in self._particles:
            a = max(40, min(200, int(180 * (p["life"] / 4.5))))
            s = pygame.Surface((int(p["r"] * 4), int(p["r"] * 4)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["c"], a), (int(p["r"] * 2), int(p["r"] * 2)), int(p["r"]))
            surface.blit(s, (int(p["x"]), int(p["y"])))

        t = pygame.time.get_ticks() * 0.001
        title = self.title_font.render(config.GAME_TITLE, True, (230, 210, 255))
        tr = title.get_rect(center=(self.vw // 2, self.vh // 4 + 20))
        shadow = self.title_font.render(config.GAME_TITLE, True, (30, 20, 45))
        surface.blit(shadow, (tr.x + 3, tr.y + 3))
        pulse = 0.92 + 0.08 * math.sin(t * 1.4)
        glow = pygame.Surface(title.get_size(), pygame.SRCALPHA)
        gt = self.title_font.render(config.GAME_TITLE, True, (200, 180, 255))
        glow.blit(gt, (0, 0))
        glow.set_alpha(int(80 * pulse))
        surface.blit(glow, (tr.x - 1, tr.y - 1))
        surface.blit(title, tr)

        sub = self.sub_font.render("Roguelike de culto e fé", True, (150, 140, 175))
        surface.blit(sub, sub.get_rect(center=(self.vw // 2, tr.bottom + 18)))

        self._btn_start, self._btn_settings, self._btn_exit = self._layout()
        labels = ("Começar", "Definições", "Sair")
        rects = (self._btn_start, self._btn_settings, self._btn_exit)
        mx, my = pygame.mouse.get_pos()
        for i, (r, lab) in enumerate(zip(rects, labels)):
            hov = r.collidepoint(mx, my)
            if hov:
                self._hover = i
            bg = (52, 42, 78) if hov else (38, 32, 58)
            br = (210, 180, 255) if hov else (110, 90, 150)
            pygame.draw.rect(surface, bg, r, border_radius=12)
            pygame.draw.rect(surface, br, r, 2, border_radius=12)
            txt = self.menu_font.render(lab, True, (245, 238, 255))
            surface.blit(txt, txt.get_rect(center=r.center))

    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        if self._btn_start and self._btn_start.collidepoint(pos):
            return "start"
        if self._btn_settings and self._btn_settings.collidepoint(pos):
            return "settings"
        if self._btn_exit and self._btn_exit.collidepoint(pos):
            return "exit"
        return None
