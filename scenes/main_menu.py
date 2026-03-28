"""
Menu principal: tema gótico e partículas subtis de fundo.
Painel de Relíquias (meta-progressão) com compra de bónus iniciais.
"""

from __future__ import annotations

import math
import random
from typing import List, Optional, Tuple

import pygame

from core import config
from core import relic_store
from core.settings_store import Settings, save_settings
from ui.font_loader import GameFonts

_DIFF_OPTIONS = (
    ("easy", "Fácil"),
    ("medium", "Médio"),
    ("hard", "Difícil"),
)


class MainMenuScene:
    def __init__(self, vw: int, vh: int, fonts: GameFonts, settings: Settings) -> None:
        self.vw = vw
        self.vh = vh
        self._settings = settings
        self.title_font = fonts.title_large
        self.menu_font = fonts.body
        self.sub_font = fonts.small
        self._particles: List[dict] = []
        self._spawn_t = 0.0
        self._btn_start: Optional[pygame.Rect] = None
        self._btn_relics: Optional[pygame.Rect] = None
        self._btn_settings: Optional[pygame.Rect] = None
        self._btn_exit: Optional[pygame.Rect] = None
        self._hover = -1
        self._relic_open = False
        self._relic_back: Optional[pygame.Rect] = None
        self._relic_buy_hp: Optional[pygame.Rect] = None
        self._relic_buy_faith: Optional[pygame.Rect] = None
        self._last_relic_msg = ""
        self._relic_msg_t = 0.0
        self._diff_easy: Optional[pygame.Rect] = None
        self._diff_med: Optional[pygame.Rect] = None
        self._diff_hard: Optional[pygame.Rect] = None

    def _layout_difficulty_buttons(self) -> None:
        cx = self.vw // 2
        cy = self.vh // 2 + 24
        tri_w, tri_gap = 96, 8
        total = 3 * tri_w + 2 * tri_gap
        dx0 = cx - total // 2
        tri_y = cy - 78
        self._diff_easy = pygame.Rect(dx0, tri_y, tri_w, 34)
        self._diff_med = pygame.Rect(dx0 + tri_w + tri_gap, tri_y, tri_w, 34)
        self._diff_hard = pygame.Rect(dx0 + 2 * (tri_w + tri_gap), tri_y, tri_w, 34)

    def on_resize(self, vw: int, vh: int) -> None:
        self.vw = vw
        self.vh = vh

    def set_fonts(self, fonts: GameFonts) -> None:
        self.title_font = fonts.title_large
        self.menu_font = fonts.body
        self.sub_font = fonts.small

    def _layout(self) -> Tuple[pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect]:
        cx, cy = self.vw // 2, self.vh // 2 + 24
        bw, bh, gap = 280, 44, 12
        rects = []
        for i in range(4):
            y = cy + i * (bh + gap)
            rects.append(pygame.Rect(cx - bw // 2, y, bw, bh))
        return (rects[0], rects[1], rects[2], rects[3])

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
        self._relic_msg_t = max(0.0, self._relic_msg_t - dt)

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

        if self._relic_open:
            self._draw_relic_panel(surface)
            return

        self._btn_start, self._btn_relics, self._btn_settings, self._btn_exit = self._layout()
        labels = ("Começar", "Relíquias", "Definições", "Sair")
        rects = (self._btn_start, self._btn_relics, self._btn_settings, self._btn_exit)
        mx, my = pygame.mouse.get_pos()
        for i, (r, lab) in enumerate(zip(rects, labels)):
            hov = r.collidepoint(mx, my)
            if hov:
                self._hover = i
            pad = 3 if hov else 0
            er = r.inflate(pad * 2, pad * 2)
            bg = (58, 48, 88) if hov else (38, 32, 58)
            br = (220, 190, 255) if hov else (110, 90, 150)
            pygame.draw.rect(surface, bg, er, border_radius=12)
            pygame.draw.rect(surface, br, er, 2, border_radius=12)
            txt = self.menu_font.render(lab, True, (245, 238, 255))
            surface.blit(txt, txt.get_rect(center=er.center))

        shard = relic_store.shard_count()
        surface.blit(
            self.sub_font.render(f"Fragmentos guardados: {shard}", True, (200, 185, 140)),
            (16, self.vh - 28),
        )

    def _draw_relic_panel(self, surface: pygame.Surface) -> None:
        vw, vh = self.vw, self.vh
        dim = pygame.Surface((vw, vh), pygame.SRCALPHA)
        dim.fill((10, 6, 20, 210))
        surface.blit(dim, (0, 0))

        meta = relic_store.load_meta()
        title = self.menu_font.render("RELÍQUIAS DO CULTO", True, (255, 220, 160))
        surface.blit(title, title.get_rect(center=(vw // 2, vh // 4)))

        y0 = vh // 4 + 48
        surface.blit(
            self.menu_font.render(f"Fragmentos: {meta.shards}", True, (230, 215, 255)),
            (vw // 2 - 200, y0),
        )
        surface.blit(
            self.sub_font.render(
                f"HP inicial +{meta.starting_hp_ranks * 4}  |  Fé inicial +{meta.starting_faith_ranks * 14}",
                True,
                (180, 170, 200),
            ),
            (vw // 2 - 200, y0 + 32),
        )

        bw, bh, gap = 320, 46, 12
        cx = vw // 2 - bw // 2
        self._relic_buy_hp = pygame.Rect(cx, y0 + 80, bw, bh)
        self._relic_buy_faith = pygame.Rect(cx, y0 + 80 + bh + gap, bw, bh)
        self._relic_back = pygame.Rect(cx, y0 + 80 + (bh + gap) * 2 + 18, bw, bh)

        mx, my = pygame.mouse.get_pos()
        for r, lab in (
            (self._relic_buy_hp, "Comprar +4 HP máx. inicial"),
            (self._relic_buy_faith, "Comprar +14 Fé ao começar"),
            (self._relic_back, "Voltar"),
        ):
            hov = r.collidepoint(mx, my)
            bg = (56, 44, 82) if hov else (40, 34, 62)
            br = (210, 175, 250) if hov else (120, 100, 155)
            pygame.draw.rect(surface, bg, r, border_radius=12)
            pygame.draw.rect(surface, br, r, 2, border_radius=12)
            t = self.menu_font.render(lab, True, (248, 242, 255))
            surface.blit(t, t.get_rect(center=r.center))

        if self._relic_msg_t > 0 and self._last_relic_msg:
            col = (160, 255, 170) if "Faltam" not in self._last_relic_msg else (255, 160, 160)
            m = self.sub_font.render(self._last_relic_msg, True, col)
            surface.blit(m, m.get_rect(center=(vw // 2, vh - 56)))

    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        if self._relic_open:
            if self._relic_back and self._relic_back.collidepoint(pos):
                self._relic_open = False
                return None
            if self._relic_buy_hp and self._relic_buy_hp.collidepoint(pos):
                _, msg = relic_store.try_buy_hp_rank()
                self._last_relic_msg = msg
                self._relic_msg_t = 3.5
                return None
            if self._relic_buy_faith and self._relic_buy_faith.collidepoint(pos):
                _, msg = relic_store.try_buy_faith_rank()
                self._last_relic_msg = msg
                self._relic_msg_t = 3.5
                return None
            return None

        self._layout_difficulty_buttons()
        if self._diff_easy and self._diff_easy.collidepoint(pos):
            self._settings.difficulty = "easy"
            save_settings(self._settings)
            return None
        if self._diff_med and self._diff_med.collidepoint(pos):
            self._settings.difficulty = "medium"
            save_settings(self._settings)
            return None
        if self._diff_hard and self._diff_hard.collidepoint(pos):
            self._settings.difficulty = "hard"
            save_settings(self._settings)
            return None

        if self._btn_start and self._btn_start.collidepoint(pos):
            return "start"
        if self._btn_relics and self._btn_relics.collidepoint(pos):
            self._relic_open = True
            return None
        if self._btn_settings and self._btn_settings.collidepoint(pos):
            return "settings"
        if self._btn_exit and self._btn_exit.collidepoint(pos):
            return "exit"
        return None
