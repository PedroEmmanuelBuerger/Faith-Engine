"""
Ecrã de definições: resolução, ecrã completo, volume.
"""

from __future__ import annotations

from typing import Callable, Optional, Tuple

import pygame

from core import config
from core.settings_store import RESOLUTION_PRESETS, Settings


class SettingsScene:
    def __init__(
        self,
        settings: Settings,
        vw: int,
        vh: int,
        on_apply: Callable[[], None],
    ) -> None:
        self.settings = settings
        self.vw = vw
        self.vh = vh
        self._on_apply = on_apply
        self.title_font = pygame.font.SysFont("segoeui", 34, bold=True)
        self.body_font = pygame.font.SysFont("segoeui", 22)
        self.small_font = pygame.font.SysFont("segoeui", 17)
        self._res_index = self._nearest_preset_index()
        self._btn_res: Optional[pygame.Rect] = None
        self._btn_full: Optional[pygame.Rect] = None
        self._slider_rect: Optional[pygame.Rect] = None
        self._btn_back: Optional[pygame.Rect] = None
        self._drag_vol = False

    def on_resize(self, vw: int, vh: int) -> None:
        self.vw = vw
        self.vh = vh

    def _nearest_preset_index(self) -> int:
        w, h = self.settings.window_width, self.settings.window_height
        best = 0
        best_d = 1e18
        for i, (pw, ph) in enumerate(RESOLUTION_PRESETS):
            d = (pw - w) ** 2 + (ph - h) ** 2
            if d < best_d:
                best_d = d
                best = i
        return best

    def _layout(self) -> None:
        cx = self.vw // 2
        y = self.vh // 3
        bw, bh, gap = 360, 44, 16
        self._btn_res = pygame.Rect(cx - bw // 2, y, bw, bh)
        self._btn_full = pygame.Rect(cx - bw // 2, y + bh + gap, bw, bh)
        self._slider_rect = pygame.Rect(cx - bw // 2, y + (bh + gap) * 2, bw, 22)
        self._btn_back = pygame.Rect(cx - bw // 2, y + (bh + gap) * 2 + 50, bw, bh)

    def _apply_resolution_preset(self) -> None:
        w, h = RESOLUTION_PRESETS[self._res_index]
        self.settings.window_width = w
        self.settings.window_height = h
        self._on_apply()

    def _set_volume_from_x(self, mx: int) -> None:
        if not self._slider_rect:
            return
        try:
            r = self._slider_rect
            t = (mx - r.x) / max(1, r.w)
            self.settings.master_volume = max(0.0, min(1.0, float(t)))
            self._on_apply()
        except (TypeError, ValueError, ArithmeticError):
            pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((18, 14, 28))
        self._layout()
        t = self.title_font.render("Definições", True, (235, 215, 255))
        surface.blit(t, t.get_rect(center=(self.vw // 2, 70)))

        assert self._btn_res and self._btn_full and self._slider_rect and self._btn_back
        w, h = RESOLUTION_PRESETS[self._res_index]
        res_label = f"Resolução: {w} × {h} (clique para mudar)"
        self._draw_button(surface, self._btn_res, res_label)

        fs = "Ecrã completo: Sim" if self.settings.fullscreen else "Ecrã completo: Não"
        self._draw_button(surface, self._btn_full, fs)

        pygame.draw.rect(surface, (40, 34, 55), self._slider_rect, border_radius=6)
        pygame.draw.rect(surface, (95, 80, 125), self._slider_rect, 2, border_radius=6)
        knob_x = self._slider_rect.x + int(self.settings.master_volume * self._slider_rect.w)
        knob = pygame.Rect(knob_x - 6, self._slider_rect.y - 4, 12, self._slider_rect.h + 8)
        pygame.draw.rect(surface, (210, 190, 255), knob, border_radius=4)

        vol_txt = self.small_font.render(
            f"Volume geral: {int(self.settings.master_volume * 100)}%",
            True,
            (190, 180, 215),
        )
        surface.blit(vol_txt, (self._slider_rect.x, self._slider_rect.y - 24))

        self._draw_button(surface, self._btn_back, "Voltar")

    def _draw_button(self, surface: pygame.Surface, r: pygame.Rect, text: str) -> None:
        mx, my = pygame.mouse.get_pos()
        hov = r.collidepoint(mx, my)
        bg = (48, 40, 72) if hov else (36, 30, 54)
        br = (190, 165, 230) if hov else (100, 85, 135)
        pygame.draw.rect(surface, bg, r, border_radius=10)
        pygame.draw.rect(surface, br, r, 2, border_radius=10)
        txt = self.body_font.render(text, True, (240, 235, 255))
        surface.blit(txt, txt.get_rect(center=r.center))

    def handle_mouse_down(self, pos: Tuple[int, int], button: int) -> Optional[str]:
        self._layout()
        assert self._btn_res and self._btn_full and self._slider_rect and self._btn_back
        if button == 1:
            if self._btn_res.collidepoint(pos):
                self._res_index = (self._res_index + 1) % len(RESOLUTION_PRESETS)
                self._apply_resolution_preset()
                return None
            if self._btn_full.collidepoint(pos):
                self.settings.fullscreen = not self.settings.fullscreen
                self._on_apply()
                return None
            if self._slider_rect.collidepoint(pos):
                self._drag_vol = True
                self._set_volume_from_x(pos[0])
                return None
            if self._btn_back.collidepoint(pos):
                return "back"
        return None

    def handle_mouse_up(self, pos: Tuple[int, int], button: int) -> None:
        self._drag_vol = False

    def handle_mouse_motion(self, pos: Tuple[int, int]) -> None:
        if self._drag_vol:
            self._set_volume_from_x(pos[0])
