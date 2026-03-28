"""
Menu de nível: três cartas clicáveis com destaque ao pairar o rato.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from core.game_state import GameState
from systems import upgrade_system


def _synergy_hint_lines(state: GameState) -> list[str]:
    lines: list[str] = []
    if state.synergy_inferno:
        lines.append("Fogo + explosão: áreas de chama e pulso maiores")
    if state.synergy_toxic_baptism:
        lines.append("Água benta + veneno: poços mais fortes e longos")
    if state.synergy_orb_velocity > 1.01 and state.upgrade_counts.get("w_celestial_orbs", 0) > 0:
        lines.append("Orbes + Passo do Véu: rotação mais rápida")
    if state.synergy_chain_echo:
        lines.append("Corrente + Eco: mais ricochetes no raio")
    if state.synergy_zeal_active:
        lines.append("Pacto de sangue + raio empilhado: zelo sombrio ativo")
    return lines


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
        card_h = 228
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
        desc_font: pygame.font.Font,
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

        rarities = getattr(state, "upgrade_choice_rarities", [])

        for i, uid in enumerate(state.upgrade_choice_ids):
            if i >= len(self.card_rects):
                break
            r = self.card_rects[i]
            hover = i == self.hovered_index
            pad = 4 if hover else 0
            r2 = r.inflate(pad * 2, pad * 2)
            rolled = rarities[i] if i < len(rarities) else upgrade_system.RARITY_COMMON
            eff = upgrade_system.effective_rarity_for_choice(uid, rolled)
            rc = upgrade_system.RARITY_RGB.get(eff, (180, 180, 200))
            bg = (52, 40, 78) if hover else (38, 30, 58)
            pygame.draw.rect(surface, bg, r2, border_radius=14)
            pygame.draw.rect(surface, rc, r2, 4 if hover else 3, border_radius=14)
            strip = pygame.Surface((r2.width - 8, 10), pygame.SRCALPHA)
            strip.fill((*rc, 120))
            surface.blit(strip, (r2.x + 4, r2.y + 6))

            name, desc = upgrade_system.describe(uid)
            stacks = state.upgrade_counts.get(uid, 0)
            ic = upgrade_system.icon_for(uid)
            rlab = upgrade_system.RARITY_LABEL_PT.get(eff, eff)
            surface.blit(
                desc_font.render(rlab.upper(), True, rc),
                (r2.x + 14, r2.y + 20),
            )
            surface.blit(
                body_font.render(f"{ic}  {name}", True, (255, 255, 255)),
                (r2.x + 14, r2.y + 36),
            )
            surface.blit(
                body_font.render(f"Próxima pilha: ×{stacks + 1}", True, (200, 190, 230)),
                (r2.x + 14, r2.y + 62),
            )
            # Descrição quebrada em linhas simples
            y = r2.y + 92
            words = desc.split()
            line = ""
            for w in words:
                test = line + w + " "
                if desc_font.size(test)[0] > r2.width - 28:
                    surface.blit(desc_font.render(line, True, (210, 200, 235)), (r2.x + 14, y))
                    y += max(18, desc_font.get_height() + 2)
                    line = w + " "
                else:
                    line = test
            if line:
                surface.blit(
                    desc_font.render(line.strip(), True, (210, 200, 235)), (r2.x + 14, y)
                )

        syn_lines = _synergy_hint_lines(state)
        if syn_lines:
            y_syn = screen_h - 28 - 20 * len(syn_lines)
            for line in syn_lines:
                syn = body_font.render(f"✦ {line}", True, (255, 190, 210))
                surface.blit(syn, syn.get_rect(center=(screen_w // 2, y_syn)))
                y_syn += 20
