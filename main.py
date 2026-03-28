"""
Culto do Infinito — loop principal (Pygame).
"""
import random

import pygame

from game_state import GameState
import ui

SCREEN_W, SCREEN_H = 960, 540
FPS = 60
BG_COLOR = (18, 14, 28)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Culto do Infinito")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("segoeui", 18)
    big = pygame.font.SysFont("segoeui", 28, bold=True)
    small = pygame.font.SysFont("segoeui", 16)

    state = GameState(SCREEN_W, SCREEN_H)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not state.level_up_paused and state.player.hp > 0:
                    state.add_click_faith()
            if event.type == pygame.KEYDOWN and state.level_up_paused:
                if event.key == pygame.K_1:
                    state.select_upgrade(0)
                elif event.key == pygame.K_2:
                    state.select_upgrade(1)
                elif event.key == pygame.K_3:
                    state.select_upgrade(2)

        keys = pygame.key.get_pressed()
        p = state.player
        if not state.level_up_paused and p.hp > 0:
            dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (
                keys[pygame.K_a] or keys[pygame.K_LEFT]
            )
            dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (
                keys[pygame.K_w] or keys[pygame.K_UP]
            )
            p.move(dx, dy, dt, SCREEN_W, SCREEN_H)
        state.update(dt)
        state.update_particles_only(dt)

        ox = oy = 0.0
        if state.screen_shake > 0.1:
            ox = random.uniform(-state.screen_shake, state.screen_shake)
            oy = random.uniform(-state.screen_shake, state.screen_shake)

        world = pygame.Surface((SCREEN_W, SCREEN_H))
        world.fill(BG_COLOR)
        ui.draw_world(world, state)
        ui.draw_particles(world, state)
        screen.blit(world, (int(ox), int(oy)))

        ui.draw_hud(screen, state, font, small)
        ui.draw_damage_flash(screen, SCREEN_W, SCREEN_H, state.damage_flash)
        if state.level_up_paused:
            ui.draw_level_up(screen, state, big, small, SCREEN_W, SCREEN_H)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
