"""
Menu de nível: três cartas clicáveis com destaque ao pairar o rato.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from core.game_state import GameState
from systems import upgrade_system


class UpgradeMenu:
    def __init__(self) -> None:
        self.card_rects: List[pygame.Rect] = []
        self.hovered_index: int = -1

    def _card_positions(
        self, n: int, screen_w: int, screen_h: int
    ) -> List[Tuple[int, int, int, int]]:
        if n <= 0:
            return []
        gap = 18
        card_w = min(260, (screen_w - gap * (n + 1)) // n)
        card_h = 210
        total_w = n * card_w + (n - 1) * gap
        start_x = (screen_w - total_w) // 2
        y = screen_h // 2 - card_h // 2
        out = []
        for i in range(n):
            x = start_x + i * (card_w + gap)
            out.append((x, y, card_w, card_h))
        return out

    def sync_layout(self, state: GameState, screen_w: int, screen_h: int) -> None:
        self.card_rects.clear()
        if not state.level_up_paused:
            self.hovered_index = -1
            return
        for x, y, w, h in self._card_positions(
            len(state.upgrade_choice_ids), screen_w, screen_h
        ):
            self.card_rects.append(pygame.Rect(x, y, w, h))

    def update_hover(self, mouse_xy: Tuple[int, int]) -> None:
        mx, my = mouse_xy
        self.hovered_index = -1
        for i, r in enumerate(self.card_rects):
            if r.collidepoint(mx, my):
                self.hovered_index = i
                break

    def click_at(self, mouse_xy: Tuple[int, int]) -> Optional[int]:
        mx, my = mouse_xy
        for i, r in enumerate(self.card_rects):
            if r.collidepoint(mx, my):
                return i
        return None

    def draw(
        self,
        surface: pygame.Surface,
        state: GameState,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        screen_w: int,
        screen_h: int,
    ) -> None:
        if not state.level_up_paused:
            return

        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((8, 4, 18, 210))
        surface.blit(overlay, (0, 0))

        t = title_font.render("RITUAL DE ASCENSÃO", True, (255, 225, 150))
        surface.blit(t, t.get_rect(center=(screen_w // 2, 56)))
        h = body_font.render("Clica numa carta para aceitar o dom", True, (200, 195, 220))
        surface.blit(h, h.get_rect(center=(screen_w // 2, 92)))

        self.sync_layout(state, screen_w, screen_h)

        for i, uid in enumerate(state.upgrade_choice_ids):
            if i >= len(self.card_rects):
                break
            r = self.card_rects[i]
            hover = i == self.hovered_index
            bg = (52, 40, 78) if hover else (38, 30, 58)
            br = (200, 170, 255) if hover else (120, 95, 160)
            pygame.draw.rect(surface, bg, r, border_radius=14)
            pygame.draw.rect(surface, br, r, 3 if hover else 2, border_radius=14)

            name, desc = upgrade_system.describe(uid)
            stacks = state.upgrade_counts.get(uid, 0)
            surface.blit(body_font.render(name, True, (255, 255, 255)), (r.x + 14, r.y + 16))
            surface.blit(
                body_font.render(f"Próxima pilha: ×{stacks + 1}", True, (200, 190, 230)),
                (r.x + 14, r.y + 44),
            )
            # Descrição quebrada em linhas simples
            y = r.y + 74
            words = desc.split()
            line = ""
            for w in words:
                test = line + w + " "
                if body_font.size(test)[0] > r.width - 28:
                    surface.blit(body_font.render(line, True, (210, 200, 235)), (r.x + 14, y))
                    y += 22
                    line = w + " "
                else:
                    line = test
            if line:
                surface.blit(body_font.render(line.strip(), True, (210, 200, 235)), (r.x + 14, y))

        if state.synergy_zeal_active:
            syn = body_font.render(
                "Sinergia: Canto Obscuro + Ritual de Sangue",
                True,
                (255, 170, 190),
            )
            surface.blit(syn, syn.get_rect(center=(screen_w // 2, screen_h - 40)))
