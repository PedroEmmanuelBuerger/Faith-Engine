"""
Culto do Infinito — loop principal (Pygame).
"""
import pygame

from game_state import GameState

SCREEN_W, SCREEN_H = 960, 540
FPS = 60
BG_COLOR = (18, 14, 28)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Culto do Infinito")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("segoeui", 18)

    state = GameState(SCREEN_W, SCREEN_H)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
        p = state.player
        p.move(dx, dy, dt, SCREEN_W, SCREEN_H)
        state.update(dt)

        screen.fill(BG_COLOR)
        for e in state.enemies:
            pygame.draw.circle(screen, (200, 80, 90), (int(e.x), int(e.y)), int(e.radius))
        pygame.draw.circle(screen, (200, 180, 255), (int(p.x), int(p.y)), p.radius)

        hud = font.render(
            f"HP {int(p.hp)}/{int(p.max_hp)}  |  Inimigos: {len(state.enemies)}  |  Onda {state.wave}",
            True,
            (230, 220, 255),
        )
        screen.blit(hud, (12, 10))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
