"""
Orquestra desenho: mundo, entidades, partículas, HUD, menu, morte.
"""

from __future__ import annotations

import math
import random
from typing import Tuple

import pygame

from core import config, utils
from core.game_state import GameState
from ui import environment, hud
from ui.player_sprites import load_player_sprites
from ui.procedural_sprites import enemy_sprite_for_kind, load_procedural_player_sprites
from ui.upgrade_menu import UpgradeMenu


def _draw_cultist_fallback(surface: pygame.Surface, sx: int, sy: int, player) -> None:
    """Placeholder se os PNGs não existirem."""
    robe = pygame.Rect(sx - 14, sy - 6, 28, 26)
    pygame.draw.ellipse(surface, (32, 28, 48), robe)
    pygame.draw.ellipse(surface, (55, 48, 72), robe, 2)
    hood = pygame.Rect(sx - 12, sy - 18, 24, 20)
    pygame.draw.ellipse(surface, (26, 22, 40), hood)
    pygame.draw.circle(surface, config.COLOR_EYE_GLOW, (sx - 5, sy - 10), 3)
    pygame.draw.circle(surface, config.COLOR_EYE_GLOW, (sx + 5, sy - 10), 3)


def _draw_player_sprite(
    surface: pygame.Surface,
    sx: int,
    sy: int,
    player,
    idle_surf: pygame.Surface | None,
    walk_frames: list[pygame.Surface] | None,
) -> None:
    """
    Parado: frente. Andando: alterna 2 frames de perfil; espelha ao ir para a esquerda.
    """
    if idle_surf is None or not walk_frames:
        _draw_cultist_fallback(surface, sx, sy, player)
        return

    if player.is_walking:
        idx = player.walk_frame % len(walk_frames)
        img = walk_frames[idx]
        if not player.facing_right:
            img = pygame.transform.flip(img, True, False)
    else:
        img = idle_surf

    rect = img.get_rect(midbottom=(int(sx), int(sy + player.radius)))
    surface.blit(img, rect)


def _draw_enemy(surface: pygame.Surface, sx: int, sy: int, enemy) -> None:
    spr = enemy_sprite_for_kind(enemy.kind)
    flash = min(1.0, enemy.hit_flash)
    h = max(28, min(58, int(enemy.radius * 2.7)))
    w = max(20, int(spr.get_width() * h / max(1, spr.get_height())))
    try:
        scaled = pygame.transform.smoothscale(spr, (w, h))
    except (pygame.error, ValueError):
        scaled = pygame.transform.scale(spr, (w, h))
    out = scaled.copy()
    if flash > 0.05:
        tint = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
        tint.fill((255, 110, 110, int(100 * flash)))
        out.blit(tint, (0, 0))
    scaled = out
    rect = scaled.get_rect(midbottom=(int(sx), int(sy + enemy.radius)))
    surface.blit(scaled, rect)
    if getattr(enemy, "charmed_until", 0) > 0:
        glow = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (120, 255, 200, 70), glow.get_rect())
        surface.blit(glow, (rect.x - 4, rect.y - 4))


def _draw_projectile(surface: pygame.Surface, sx: int, sy: int, kind: str) -> None:
    if kind == "holy_flask":
        pygame.draw.circle(surface, (140, 220, 255), (sx, sy), 10)
        pygame.draw.circle(surface, (220, 255, 255), (sx, sy), 5)
    else:
        pygame.draw.circle(surface, config.COLOR_PROJECTILE_GLOW, (sx, sy), 9)
        pygame.draw.circle(surface, config.COLOR_PROJECTILE_CORE, (sx, sy), 5)


class UIManager:
    def __init__(self) -> None:
        self.upgrade_menu = UpgradeMenu()
        self.title_font = pygame.font.SysFont("segoeui", 28, bold=True)
        self.big_death_font = pygame.font.SysFont("segoeui", 52, bold=True)
        self.hud_font = pygame.font.SysFont("segoeui", 18)
        self.small_font = pygame.font.SysFont("segoeui", 15)
        self._player_idle, self._player_walk_frames = load_player_sprites()
        if self._player_idle is None or not self._player_walk_frames:
            self._player_idle, self._player_walk_frames = load_procedural_player_sprites()
        self.death_restart_rect: pygame.Rect | None = None
        self.death_menu_rect: pygame.Rect | None = None
        self.pause_resume_rect: pygame.Rect | None = None
        self.pause_menu_rect: pygame.Rect | None = None
        self.pause_exit_rect: pygame.Rect | None = None

    def draw_world_layer(self, surface: pygame.Surface, state: GameState) -> None:
        cx, cy = state.camera_x, state.camera_y
        environment.draw_world_background(surface, state)

        for pool in state.ground_pools:
            psx, psy = utils.world_to_screen(pool["x"], pool["y"], cx, cy)
            r = int(pool["radius"])
            s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (120, 200, 255, 55), (r + 2, r + 2), r)
            pygame.draw.circle(s, (200, 255, 240, 110), (r + 2, r + 2), max(4, r // 4))
            surface.blit(s, (int(psx - r - 2), int(psy - r - 2)))

        for ox, oy in state.orbital_debug:
            osx, osy = utils.world_to_screen(ox, oy, cx, cy)
            pygame.draw.circle(surface, (255, 230, 160), (int(osx), int(osy)), 10)
            pygame.draw.circle(surface, (255, 255, 220), (int(osx), int(osy)), 4)

        p = state.player
        for sw in state.melee_swings:
            ang = sw["angle"]
            ha = sw["half_arc"]
            rng = int(sw["range"])
            psx, psy = utils.world_to_screen(p.x, p.y, cx, cy)
            rect = pygame.Rect(psx - rng - 4, psy - rng - 4, (rng + 4) * 2, (rng + 4) * 2)
            surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            cx0, cy0 = rng + 4, rng + 4
            a0 = ang - ha
            a1 = ang + ha
            pts = [(cx0, cy0)]
            steps = 10
            for i in range(steps + 1):
                t = i / steps
                a = a0 + (a1 - a0) * t
                pts.append((cx0 + math.cos(a) * rng, cy0 + math.sin(a) * rng))
            pygame.draw.polygon(surf, (255, 220, 180, 70), pts)
            surface.blit(surf, rect.topleft)

        for e in state.enemies:
            sx, sy = utils.world_to_screen(e.x, e.y, cx, cy)
            if -50 < sx < config.VIEWPORT_W + 50 and -50 < sy < config.VIEWPORT_H + 50:
                _draw_enemy(surface, int(sx), int(sy), e)

        for proj in state.projectiles:
            sx, sy = utils.world_to_screen(proj.x, proj.y, cx, cy)
            if -20 < sx < config.VIEWPORT_W + 20:
                _draw_projectile(surface, int(sx), int(sy), proj.kind)

        for b in state.enemy_bullets:
            bx, by = utils.world_to_screen(b["x"], b["y"], cx, cy)
            pygame.draw.circle(surface, (255, 100, 90), (int(bx), int(by)), 5)

        sx, sy = utils.world_to_screen(p.x, p.y, cx, cy)
        _draw_player_sprite(
            surface, int(sx), int(sy), p, self._player_idle, self._player_walk_frames
        )

        for pt in state.particles:
            psx, psy = utils.world_to_screen(pt["x"], pt["y"], cx, cy)
            life = max(0.12, min(0.6, pt["life"]))
            alpha = max(40, min(255, int(255 * (life / 0.6))))
            col = pt["col"]
            px = pygame.Surface((8, 8), pygame.SRCALPHA)
            px.fill((*col, alpha))
            surface.blit(px, (int(psx - 4), int(psy - 4)))

    def draw_damage_flash(
        self, surface: pygame.Surface, amount: float
    ) -> None:
        if amount <= 0.02:
            return
        red = pygame.Surface((config.VIEWPORT_W, config.VIEWPORT_H), pygame.SRCALPHA)
        red.fill((160, 30, 55, int(130 * amount)))
        surface.blit(red, (0, 0))

    def draw_death_screen(self, surface: pygame.Surface, state: GameState) -> None:
        if state.death_mode == "alive":
            self.death_restart_rect = None
            self.death_menu_rect = None
            return
        dark = pygame.Surface((config.VIEWPORT_W, config.VIEWPORT_H), pygame.SRCALPHA)
        a = int(220 * state.death_fade)
        dark.fill((10, 4, 14, a))
        surface.blit(dark, (0, 0))

        if state.death_mode == "await_click" or state.death_fade > 0.35:
            title = self.big_death_font.render("A LUZ EXPIROU", True, (240, 220, 200))
            r = title.get_rect(center=(config.VIEWPORT_W // 2, config.VIEWPORT_H // 2 - 70))
            shadow = self.big_death_font.render("A LUZ EXPIROU", True, (40, 20, 30))
            surface.blit(shadow, (r.x + 3, r.y + 3))
            surface.blit(title, r)

            f = self.hud_font.render(f"Fé final: {int(state.faith)}", True, (220, 200, 230))
            surface.blit(f, f.get_rect(center=(config.VIEWPORT_W // 2, config.VIEWPORT_H // 2 - 5)))
            lv = self.hud_font.render(f"Nível alcançado: {state.level}", True, (200, 185, 220))
            surface.blit(lv, lv.get_rect(center=(config.VIEWPORT_W // 2, config.VIEWPORT_H // 2 + 28)))

            if state.death_mode == "await_click":
                cy = config.VIEWPORT_H // 2 + 88
                bw, bh = 220, 44
                gap = 18
                total = bw * 2 + gap
                sx0 = (config.VIEWPORT_W - total) // 2
                self.death_restart_rect = pygame.Rect(sx0, cy, bw, bh)
                self.death_menu_rect = pygame.Rect(sx0 + bw + gap, cy, bw, bh)
                for r, label in (
                    (self.death_restart_rect, "Recomeçar"),
                    (self.death_menu_rect, "Menu principal"),
                ):
                    pygame.draw.rect(surface, (48, 38, 72), r, border_radius=10)
                    pygame.draw.rect(surface, (180, 150, 220), r, 2, border_radius=10)
                    t = self.hud_font.render(label, True, (240, 230, 255))
                    surface.blit(t, t.get_rect(center=r.center))
            else:
                self.death_restart_rect = None
                self.death_menu_rect = None

    def draw_frame(self, screen: pygame.Surface, state: GameState) -> None:
        if not state.game_paused:
            self.pause_resume_rect = None
            self.pause_menu_rect = None
            self.pause_exit_rect = None
        world = pygame.Surface((config.VIEWPORT_W, config.VIEWPORT_H))
        self.draw_world_layer(world, state)

        ox = oy = 0.0
        if state.screen_shake > 0.08:
            ox = random.uniform(-state.screen_shake, state.screen_shake)
            oy = random.uniform(-state.screen_shake, state.screen_shake)

        screen.blit(world, (int(ox), int(oy)))
        hud.draw_hud(screen, state, self.hud_font, self.small_font)
        self.draw_damage_flash(screen, state.damage_flash)
        self.upgrade_menu.draw(
            screen,
            state,
            self.title_font,
            self.small_font,
            config.VIEWPORT_W,
            config.VIEWPORT_H,
        )
        if state.game_paused and state.death_mode == "alive":
            self.draw_pause_overlay(screen)
        self.draw_death_screen(screen, state)

    def draw_pause_overlay(self, surface: pygame.Surface) -> None:
        vw, vh = config.VIEWPORT_W, config.VIEWPORT_H
        dim = pygame.Surface((vw, vh), pygame.SRCALPHA)
        dim.fill((8, 4, 18, 200))
        surface.blit(dim, (0, 0))
        title = self.title_font.render("PAUSA", True, (240, 220, 255))
        tr = title.get_rect(center=(vw // 2, vh // 3))
        surface.blit(title, tr)

        bw, bh, gap = 260, 46, 14
        cx = vw // 2 - bw // 2
        y0 = tr.bottom + 36
        self.pause_resume_rect = pygame.Rect(cx, y0, bw, bh)
        self.pause_menu_rect = pygame.Rect(cx, y0 + bh + gap, bw, bh)
        self.pause_exit_rect = pygame.Rect(cx, y0 + (bh + gap) * 2, bw, bh)
        for r, label in (
            (self.pause_resume_rect, "Continuar"),
            (self.pause_menu_rect, "Menu principal"),
            (self.pause_exit_rect, "Sair do jogo"),
        ):
            pygame.draw.rect(surface, (44, 36, 68), r, border_radius=12)
            pygame.draw.rect(surface, (190, 165, 230), r, 2, border_radius=12)
            t = self.hud_font.render(label, True, (245, 238, 255))
            surface.blit(t, t.get_rect(center=r.center))

    def handle_upgrade_hover(self, mouse_xy: Tuple[int, int], state: GameState) -> None:
        if state.level_up_paused:
            self.upgrade_menu.sync_layout(state, config.VIEWPORT_W, config.VIEWPORT_H)
            self.upgrade_menu.update_hover(mouse_xy)
