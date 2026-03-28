"""
HUD: barras, texto, transcendência (sem mundo).
"""

from __future__ import annotations

import pygame

from core import config
from core.game_state import GameState
from systems import upgrade_system


def draw_hud(
    surface: pygame.Surface,
    state: GameState,
    font: pygame.font.Font,
    small: pygame.font.Font,
) -> None:
    p = state.player
    xp_frac = min(1.0, state.xp / max(1.0, state.xp_to_next))
    bar_w = 200
    pygame.draw.rect(surface, (32, 26, 48), (12, 38, bar_w, 8))
    pygame.draw.rect(surface, (100, 180, 130), (12, 38, int(bar_w * xp_frac), 8))

    wname, _ = upgrade_system.describe(state.active_weapon_id)
    loadout_icons = " ".join(upgrade_system.icon_for(w) for w in state.weapon_loadout)
    line = (
        f"HP {int(p.hp)}/{int(p.max_hp)}  |  Fé {int(state.faith)}  |  "
        f"Nv {state.level}  |  XP {int(state.xp)}/{int(state.xp_to_next)}  |  "
        f"Inimigos {len(state.enemies)}  |  Onda {state.wave}"
    )
    surface.blit(font.render(line, True, (230, 220, 255)), (12, 10))
    auto_on = state.auto_attack_enabled
    auto_lbl = "AUTO" if auto_on else "MANUAL"
    auto_col = (150, 255, 170) if auto_on else (190, 175, 215)
    bx = config.VIEWPORT_W - 132
    pygame.draw.rect(surface, (36, 30, 52), (bx, 8, 124, 24))
    pygame.draw.rect(surface, auto_col, (bx, 8, 124, 24), 2)
    surface.blit(small.render(f"Mira: {auto_lbl}", True, auto_col), (bx + 8, 11))
    surface.blit(
        small.render(
            f"Armas [{loadout_icons}]  ·  foco {upgrade_system.icon_for(state.active_weapon_id)} {wname}  |  "
            "Dir.: auto-ataque  |  Meio: Fé  |  WASD",
            True,
            (170, 160, 200),
        ),
        (12, 52),
    )
    surface.blit(
        small.render(
            f"Pressão de spawn: ×{state.spawn_pressure:.2f}",
            True,
            (150, 140, 180),
        ),
        (280, 72),
    )
    trans = f"Transcendência {state.prestige_points} (+{int(state.prestige_faith_mult * 100 - 100)}% Fé)"
    surface.blit(small.render(trans, True, (210, 190, 150)), (480, 52))

    buff_parts: list[str] = []
    uc = state.upgrade_counts
    if uc.get("blood_pact", 0) > 0:
        buff_parts.append(upgrade_system.icon_for("blood_pact"))
    if uc.get("fervor", 0) > 0:
        buff_parts.append(upgrade_system.icon_for("fervor"))
    if uc.get("omen_sight", 0) > 0:
        buff_parts.append(upgrade_system.icon_for("omen_sight"))
    if uc.get("veil_step", 0) > 0:
        buff_parts.append(upgrade_system.icon_for("veil_step"))
    if uc.get("chain_lightning", 0) > 0:
        buff_parts.append(upgrade_system.icon_for("chain_lightning"))
    if buff_parts:
        ap = float(getattr(state, "ascension_pick_bonus", 0.0))
        bonus_txt = f"  |  Ascensão +{int(ap * 100)}% dano" if ap > 0.001 else ""
        surface.blit(
            small.render("Poder ativo: " + " ".join(buff_parts) + bonus_txt, True, (255, 210, 175)),
            (12, config.VIEWPORT_H - 50),
        )

    if state.can_prestige():
        surface.blit(
            small.render("[P] Transcender (≥400 Fé)", True, (240, 210, 130)),
            (12, config.VIEWPORT_H - 26),
        )

    y = 72
    if state.upgrade_counts:
        surface.blit(small.render("Domínios:", True, (200, 190, 255)), (12, y))
        y += 20
        for uid, n in sorted(state.upgrade_counts.items()):
            name, _ = upgrade_system.describe(uid)
            surface.blit(small.render(f" · {name} x{n}", True, (185, 175, 225)), (12, y))
            y += 17
