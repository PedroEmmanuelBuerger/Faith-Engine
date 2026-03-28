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
    big = pygame.font.SysFont("segoeui", 32, bold=True)

    state = GameState(SCREEN_W, SCREEN_H)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if state.level_up_paused:
                    state.acknowledge_level_up_placeholder()

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

        screen.fill(BG_COLOR)
        for e in state.enemies:
            pygame.draw.circle(screen, (200, 80, 90), (int(e.x), int(e.y)), int(e.radius))
        pygame.draw.circle(screen, (200, 180, 255), (int(p.x), int(p.y)), p.radius)

        xp_frac = min(1.0, state.xp / max(1.0, state.xp_to_next))
        bar_w = 220
        pygame.draw.rect(screen, (40, 32, 55), (12, 36, bar_w, 10))
        pygame.draw.rect(screen, (120, 200, 140), (12, 36, int(bar_w * xp_frac), 10))

        hud = font.render(
            f"HP {int(p.hp)}/{int(p.max_hp)}  |  Nv {state.level}  |  XP {int(state.xp)}/{int(state.xp_to_next)}  |  Inimigos: {len(state.enemies)}  |  Onda {state.wave}",
            True,
            (230, 220, 255),
        )
        screen.blit(hud, (12, 10))

        if state.level_up_paused:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 170))
            screen.blit(ov, (0, 0))
            t1 = big.render("EVOLUÇÃO", True, (255, 230, 120))
            t2 = font.render("Espaço: absorver energia (+HP máx / cura)", True, (220, 220, 240))
            screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30)))
            screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 20)))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
