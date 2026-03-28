"""
Culto do Infinito — loop principal (Pygame).
"""
import pygame

from game_state import GameState
import upgrades

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

        screen.fill(BG_COLOR)
        for e in state.enemies:
            pygame.draw.circle(screen, (200, 80, 90), (int(e.x), int(e.y)), int(e.radius))
        pygame.draw.circle(screen, (200, 180, 255), (int(p.x), int(p.y)), p.radius)

        xp_frac = min(1.0, state.xp / max(1.0, state.xp_to_next))
        bar_w = 220
        pygame.draw.rect(screen, (40, 32, 55), (12, 36, bar_w, 10))
        pygame.draw.rect(screen, (120, 200, 140), (12, 36, int(bar_w * xp_frac), 10))

        hud = font.render(
            f"HP {int(p.hp)}/{int(p.max_hp)}  |  Fé {int(state.faith)}  |  Nv {state.level}  |  XP {int(state.xp)}/{int(state.xp_to_next)}  |  Inimigos: {len(state.enemies)}  |  Onda {state.wave}",
            True,
            (230, 220, 255),
        )
        screen.blit(hud, (12, 10))
        sub = small.render("Clique esquerdo: ganhar Fé", True, (180, 170, 210))
        screen.blit(sub, (12, 52))

        if state.level_up_paused:
            ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 175))
            screen.blit(ov, (0, 0))
            title = big.render("RITUAL DE ASCENSÃO", True, (255, 230, 140))
            screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 80)))
            hint = small.render("Teclas 1, 2 ou 3 para escolher o dom", True, (200, 200, 220))
            screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, 118)))
            y = 160
            for i, uid in enumerate(state.upgrade_choice_ids):
                name, desc = upgrades.describe(uid)
                card = pygame.Rect(80 + i * 280, y, 250, 200)
                pygame.draw.rect(screen, (48, 36, 72), card, border_radius=12)
                pygame.draw.rect(screen, (140, 110, 200), card, 2, border_radius=12)
                key_lbl = small.render(f"[{i + 1}]", True, (255, 220, 160))
                screen.blit(key_lbl, (card.x + 12, card.y + 10))
                nl = small.render(name, True, (255, 255, 255))
                screen.blit(nl, (card.x + 12, card.y + 36))
                stacks = state.upgrade_counts.get(uid, 0)
                st = small.render(f"Pilha: x{stacks + 1} (próximo)", True, (200, 190, 230))
                screen.blit(st, (card.x + 12, card.y + 62))
                wrapped = desc
                bl = small.render(wrapped, True, (210, 200, 235))
                screen.blit(bl, (card.x + 12, card.y + 92))
            if state.synergy_zeal_active:
                syn = small.render("Sinergia ativa: Canto + Ritual amplificam o dano.", True, (255, 180, 200))
                screen.blit(syn, syn.get_rect(center=(SCREEN_W // 2, SCREEN_H - 48)))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
