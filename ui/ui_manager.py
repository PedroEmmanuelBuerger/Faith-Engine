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
from entities.enemy import EnemyKind
from ui import environment, hud
from ui.player_sprites import load_player_sprites
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
    walk_surf: pygame.Surface | None,
) -> None:
    """
    Parado: sprite de frente. Andando: sprite de perfil (espelhado se for para a esquerda).
    Ancoragem: pés na base do círculo de colisão.
    """
    if idle_surf is None or walk_surf is None:
        _draw_cultist_fallback(surface, sx, sy, player)
        return

    if player.is_walking:
        img = walk_surf
        if not player.facing_right:
            img = pygame.transform.flip(walk_surf, True, False)
    else:
        img = idle_surf

    rect = img.get_rect(midbottom=(int(sx), int(sy + player.radius)))
    surface.blit(img, rect)


def _draw_enemy(surface: pygame.Surface, sx: int, sy: int, enemy) -> None:
    flash = min(1.0, enemy.hit_flash)
    if enemy.kind == EnemyKind.POSSESSED_STATUE:
        base = (100 + int(40 * flash), 95 + int(35 * flash), 115 + int(30 * flash))
        body = pygame.Rect(sx - 16, sy - 20, 32, 36)
        pygame.draw.rect(surface, base, body, border_radius=4)
        pygame.draw.rect(surface, config.COLOR_STONE_LIGHT, body, 2, border_radius=4)
        pygame.draw.circle(surface, config.COLOR_GOLD_DIM, (sx, sy - 24), 6)
    elif enemy.kind == EnemyKind.SHADOW_CREATURE:
        pygame.draw.ellipse(surface, (35, 28, 55), (sx - 18, sy - 12, 36, 24))
        pygame.draw.ellipse(surface, (80, 50, 120), (sx - 18, sy - 12, 36, 24), 2)
        pygame.draw.circle(surface, (200, 60, 80), (sx - 6, sy - 4), 2)
        pygame.draw.circle(surface, (200, 60, 80), (sx + 6, sy - 4), 2)
    else:
        # Sacerdote corrupto — manto bordô
        pygame.draw.ellipse(surface, (90 + int(40 * flash), 35, 50), (sx - 14, sy - 14, 28, 30))
        pygame.draw.rect(surface, (55, 45, 70), (sx - 10, sy + 2, 20, 18), border_radius=3)
        pygame.draw.circle(surface, (200, 200, 220), (sx, sy - 8), 5)
        pygame.draw.circle(surface, (255, 80, 90), (sx - 2, sy - 8), 2)


def _draw_projectile(surface: pygame.Surface, sx: int, sy: int) -> None:
    pygame.draw.circle(surface, config.COLOR_PROJECTILE_GLOW, (sx, sy), 9)
    pygame.draw.circle(surface, config.COLOR_PROJECTILE_CORE, (sx, sy), 5)


class UIManager:
    def __init__(self) -> None:
        self.upgrade_menu = UpgradeMenu()
        self.title_font = pygame.font.SysFont("segoeui", 28, bold=True)
        self.big_death_font = pygame.font.SysFont("segoeui", 52, bold=True)
        self.hud_font = pygame.font.SysFont("segoeui", 18)
        self.small_font = pygame.font.SysFont("segoeui", 15)
        self._player_idle, self._player_walk = load_player_sprites()

    def draw_world_layer(self, surface: pygame.Surface, state: GameState) -> None:
        cx, cy = state.camera_x, state.camera_y
        environment.draw_world_background(surface, cx, cy)

        for e in state.enemies:
            sx, sy = utils.world_to_screen(e.x, e.y, cx, cy)
            if -50 < sx < config.VIEWPORT_W + 50 and -50 < sy < config.VIEWPORT_H + 50:
                _draw_enemy(surface, int(sx), int(sy), e)

        for proj in state.projectiles:
            sx, sy = utils.world_to_screen(proj.x, proj.y, cx, cy)
            if -20 < sx < config.VIEWPORT_W + 20:
                _draw_projectile(surface, int(sx), int(sy))

        p = state.player
        sx, sy = utils.world_to_screen(p.x, p.y, cx, cy)
        _draw_player_sprite(
            surface, int(sx), int(sy), p, self._player_idle, self._player_walk
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
                pulse = 0.75 + 0.25 * math.sin(pygame.time.get_ticks() * 0.005)
                c = (int(200 + 55 * pulse), int(220 + 35 * pulse), 255)
                hint = self.title_font.render("Clica para reencarnar", True, c)
                surface.blit(hint, hint.get_rect(center=(config.VIEWPORT_W // 2, config.VIEWPORT_H // 2 + 95)))

    def draw_frame(self, screen: pygame.Surface, state: GameState) -> None:
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
        self.draw_death_screen(screen, state)

    def handle_upgrade_hover(self, mouse_xy: Tuple[int, int], state: GameState) -> None:
        if state.level_up_paused:
            self.upgrade_menu.sync_layout(state, config.VIEWPORT_W, config.VIEWPORT_H)
            self.upgrade_menu.update_hover(mouse_xy)
