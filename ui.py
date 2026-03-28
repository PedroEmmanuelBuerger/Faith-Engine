"""
Interface Pygame: mundo, HUD e painel de upgrades.
"""

from __future__ import annotations

import pygame

import upgrades
from game_state import GameState


def draw_particles(surface: pygame.Surface, state: GameState) -> None:
    """Partículas ao eliminar inimigos."""
    for pt in state.particles:
        alpha = max(40, min(255, int(255 * min(1.0, pt["life"] / 0.5))))
        c = pt["col"]
        px = pygame.Surface((8, 8), pygame.SRCALPHA)
        px.fill((*c, alpha))
        surface.blit(px, (int(pt["x"] - 4), int(pt["y"] - 4)))


def draw_world(surface: pygame.Surface, state: GameState) -> None:
    """Inimigos e jogador."""
    for e in state.enemies:
        pygame.draw.circle(
            surface, (200, 80, 90), (int(e.x), int(e.y)), int(e.radius)
        )
    p = state.player
    pygame.draw.circle(surface, (200, 180, 255), (int(p.x), int(p.y)), p.radius)


def draw_hud(
    surface: pygame.Surface,
    state: GameState,
    font: pygame.font.Font,
    small: pygame.font.Font,
) -> None:
    """Barras e texto principal."""
    p = state.player
    xp_frac = min(1.0, state.xp / max(1.0, state.xp_to_next))
    bar_w = 220
    pygame.draw.rect(surface, (40, 32, 55), (12, 36, bar_w, 10))
    pygame.draw.rect(surface, (120, 200, 140), (12, 36, int(bar_w * xp_frac), 10))

    line = (
        f"HP {int(p.hp)}/{int(p.max_hp)}  |  Fé {int(state.faith)}  |  "
        f"Nv {state.level}  |  XP {int(state.xp)}/{int(state.xp_to_next)}  |  "
        f"Inimigos: {len(state.enemies)}  |  Onda {state.wave}"
    )
    surface.blit(font.render(line, True, (230, 220, 255)), (12, 10))
    surface.blit(
        small.render("Clique esquerdo: ganhar Fé", True, (180, 170, 210)), (12, 52)
    )
    surface.blit(
        small.render(
            f"Pressão do vazio: x{state.difficulty_mult:.2f}",
            True,
            (160, 150, 190),
        ),
        (240, 52),
    )

    # Lista compacta de upgrades ativos
    y = 72
    if state.upgrade_counts:
        surface.blit(small.render("Domínios:", True, (200, 190, 255)), (12, y))
        y += 22
        for uid, n in sorted(state.upgrade_counts.items()):
            name, _ = upgrades.describe(uid)
            surface.blit(
                small.render(f"  · {name} x{n}", True, (190, 185, 230)),
                (12, y),
            )
            y += 18


def draw_level_up(
    surface: pygame.Surface,
    state: GameState,
    big: pygame.font.Font,
    small: pygame.font.Font,
    screen_w: int,
    screen_h: int,
) -> None:
    """Três cartas de escolha."""
    ov = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 175))
    surface.blit(ov, (0, 0))
    title = big.render("RITUAL DE ASCENSÃO", True, (255, 230, 140))
    surface.blit(title, title.get_rect(center=(screen_w // 2, 80)))
    hint = small.render("Teclas 1, 2 ou 3 para escolher o dom", True, (200, 200, 220))
    surface.blit(hint, hint.get_rect(center=(screen_w // 2, 118)))
    y = 160
    for i, uid in enumerate(state.upgrade_choice_ids):
        name, desc = upgrades.describe(uid)
        card = pygame.Rect(80 + i * 280, y, 250, 200)
        pygame.draw.rect(surface, (48, 36, 72), card, border_radius=12)
        pygame.draw.rect(surface, (140, 110, 200), card, 2, border_radius=12)
        surface.blit(small.render(f"[{i + 1}]", True, (255, 220, 160)), (card.x + 12, card.y + 10))
        surface.blit(small.render(name, True, (255, 255, 255)), (card.x + 12, card.y + 36))
        stacks = state.upgrade_counts.get(uid, 0)
        surface.blit(
            small.render(f"Pilha: x{stacks + 1} (próximo)", True, (200, 190, 230)),
            (card.x + 12, card.y + 62),
        )
        surface.blit(small.render(desc, True, (210, 200, 235)), (card.x + 12, card.y + 92))
    if state.synergy_zeal_active:
        syn = small.render(
            "Sinergia ativa: Canto Obscuro + Ritual de Sangue amplificam o dano.",
            True,
            (255, 180, 200),
        )
        surface.blit(syn, syn.get_rect(center=(screen_w // 2, screen_h - 48)))


def draw_damage_flash(surface: pygame.Surface, screen_w: int, screen_h: int, amount: float) -> None:
    """Vermelho translúcido ao receber dano."""
    if amount <= 0.02:
        return
    red = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    red.fill((180, 40, 60, int(120 * amount)))
    surface.blit(red, (0, 0))
