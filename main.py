"""
Faith-Engine — ponto de entrada.
"""
import pygame

from core import config
from core.game_state import GameState
from ui.ui_manager import UIManager


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((config.VIEWPORT_W, config.VIEWPORT_H))
    pygame.display.set_caption(config.GAME_TITLE)
    clock = pygame.time.Clock()

    state = GameState()
    ui = UIManager()
    running = True

    while running:
        dt = clock.tick(config.FPS) / 1000.0
        mouse = pygame.mouse.get_pos()
        ui.handle_upgrade_hover(mouse, state)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if state.death_mode == "await_click":
                        state.reset_run(keep_meta=True)
                    elif state.level_up_paused:
                        idx = ui.upgrade_menu.click_at(event.pos)
                        if idx is not None:
                            state.select_upgrade(idx)

                if event.button == 3:
                    if (
                        state.death_mode == "alive"
                        and state.player.hp > 0
                        and not state.level_up_paused
                    ):
                        state.add_click_faith()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and state.death_mode == "alive":
                    state.do_prestige()

        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
        state.move_player(dx, dy, dt)

        state.update(dt)
        ui.draw_frame(screen, state)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
