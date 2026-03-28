"""
Culto do Infinito — loop principal (Pygame).
"""
import pygame

from player import Player

SCREEN_W, SCREEN_H = 960, 540
FPS = 60
BG_COLOR = (18, 14, 28)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Culto do Infinito")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("segoeui", 18)

    player = Player(SCREEN_W / 2, SCREEN_H / 2)
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
        player.move(dx, dy, dt, SCREEN_W, SCREEN_H)

        screen.fill(BG_COLOR)
        pygame.draw.circle(
            screen, (200, 180, 255), (int(player.x), int(player.y)), player.radius
        )

        hud = font.render(
            f"HP {int(player.hp)}/{int(player.max_hp)}  |  Dano {player.effective_damage:.0f}  |  Alcance {player.effective_range:.0f}",
            True,
            (230, 220, 255),
        )
        screen.blit(hud, (12, 10))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
