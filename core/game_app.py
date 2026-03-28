"""
Gestor de cenas: menu, definições, jogo, game over.
"""

from __future__ import annotations

from enum import Enum, auto

import pygame

from core import config, display, game_logging, sfx
from core.audio_manager import AudioManager
from core.game_state import GameState
from core.settings_store import Settings, default_settings, load_settings, save_settings
from systems import upgrade_system
from scenes.main_menu import MainMenuScene
from scenes.settings_scene import SettingsScene
from ui.ui_manager import UIManager

_log = game_logging.get_logger("app")


class AppScene(Enum):
    MAIN_MENU = auto()
    SETTINGS = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class GameApp:
    def __init__(self) -> None:
        try:
            pygame.mixer.pre_init(44100, -16, 2, 2048)
        except pygame.error:
            _log.warning("mixer.pre_init falhou (continuar sem pré-inicialização)")
        pygame.init()
        pygame.display.set_caption(config.GAME_TITLE)

        try:
            self.settings: Settings = load_settings()
        except Exception as e:
            _log.error("Erro inesperado ao carregar definições: %s", e)
            self.settings = default_settings()

        try:
            self.screen = display.apply_video_mode(
                self.settings.window_width,
                self.settings.window_height,
                self.settings.fullscreen,
            )
        except (pygame.error, OSError) as e:
            _log.error("Falha ao criar janela: %s — a tentar 1280×720 janela", e)
            self.settings.fullscreen = False
            self.settings.window_width = 1280
            self.settings.window_height = 720
            self.screen = display.apply_video_mode(1280, 720, False)
        self._sync_settings_size_from_screen()

        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = AppScene.MAIN_MENU
        game_logging.log_state("Cena: MAIN_MENU")

        self.audio = AudioManager()
        self.audio.init_mixer()
        self.audio.load_all()
        sfx.bind(self.audio)
        self.audio.set_master_volume(self.settings.master_volume)
        self.audio.play_music_loop()
        if not self.audio._mixer_ok:
            _log.warning("Áudio desativado (mixer indisponível)")

        vw, vh = self.screen.get_size()
        self.main_menu = MainMenuScene(vw, vh)
        self.settings_scene: SettingsScene | None = None
        self.play_state: GameState | None = None
        self.saved_prestige_points: int = 0
        self.ui = UIManager()

    def _sync_settings_size_from_screen(self) -> None:
        w, h = self.screen.get_size()
        self.settings.window_width = w
        self.settings.window_height = h

    def _apply_settings(self) -> None:
        try:
            self.screen = display.apply_video_mode(
                self.settings.window_width,
                self.settings.window_height,
                self.settings.fullscreen,
            )
        except (pygame.error, OSError) as e:
            _log.warning("Reaplicar vídeo falhou: %s", e)
            return
        self._sync_settings_size_from_screen()
        config.set_viewport(*self.screen.get_size())
        vw, vh = config.VIEWPORT_W, config.VIEWPORT_H
        self.main_menu.on_resize(vw, vh)
        if self.settings_scene:
            self.settings_scene.on_resize(vw, vh)
        try:
            self.audio.set_master_volume(self.settings.master_volume)
        except Exception as e:
            _log.warning("Volume não aplicado: %s", e)
        save_settings(self.settings)

    def _open_settings(self) -> None:
        self.settings_scene = SettingsScene(
            self.settings,
            config.VIEWPORT_W,
            config.VIEWPORT_H,
            self._apply_settings,
        )
        self.scene = AppScene.SETTINGS
        game_logging.log_state("Cena: SETTINGS")

    def _start_play(self) -> None:
        self.play_state = GameState()
        if self.saved_prestige_points > 0:
            self.play_state.prestige_points = self.saved_prestige_points
            self.play_state.prestige_faith_mult = 1.0 + 0.12 * self.saved_prestige_points
            upgrade_system.refresh_stats(self.play_state)
        self.scene = AppScene.PLAYING
        game_logging.log_state("Cena: PLAYING (nova run)")

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(self.settings)
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.settings.fullscreen = not self.settings.fullscreen
                    self._apply_settings()
                if self.scene == AppScene.PLAYING and self.play_state:
                    st = self.play_state
                    if event.key == pygame.K_ESCAPE:
                        if (
                            st.death_mode == "alive"
                            and not st.level_up_paused
                            and st.player.hp > 0
                        ):
                            st.game_paused = not st.game_paused
                            game_logging.log_state(
                                "Pausa: %s" % ("ligada" if st.game_paused else "desligada")
                            )
                    elif event.key == pygame.K_p and st.death_mode == "alive" and not st.game_paused:
                        st.do_prestige()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._on_mouse_down(event.pos, event.button)

            if event.type == pygame.MOUSEBUTTONUP:
                if self.scene == AppScene.SETTINGS and self.settings_scene:
                    self.settings_scene.handle_mouse_up(event.pos, event.button)

            if event.type == pygame.MOUSEMOTION:
                if self.scene == AppScene.SETTINGS and self.settings_scene:
                    self.settings_scene.handle_mouse_motion(event.pos)

    def _on_mouse_down(self, pos: tuple[int, int], button: int) -> None:
        if button != 1:
            if (
                button == 3
                and self.scene == AppScene.PLAYING
                and self.play_state
                and self.play_state.death_mode == "alive"
                and self.play_state.player.hp > 0
                and not self.play_state.level_up_paused
                and not self.play_state.game_paused
            ):
                self.play_state.add_click_faith()
            return

        if self.scene == AppScene.PLAYING and self.play_state:
            st = self.play_state
            if st.game_paused and st.death_mode == "alive":
                r0, r1, r2 = (
                    self.ui.pause_resume_rect,
                    self.ui.pause_menu_rect,
                    self.ui.pause_exit_rect,
                )
                if r0 and r0.collidepoint(pos):
                    st.game_paused = False
                    game_logging.log_state("Pausa: continuar")
                elif r1 and r1.collidepoint(pos):
                    st.game_paused = False
                    self.saved_prestige_points = st.prestige_points
                    self.play_state = None
                    self.scene = AppScene.MAIN_MENU
                    game_logging.log_state("Cena: MAIN_MENU (desde pausa)")
                elif r2 and r2.collidepoint(pos):
                    save_settings(self.settings)
                    self.running = False
                    game_logging.log_state("Sair (desde pausa)")
                return

        if self.scene == AppScene.MAIN_MENU:
            act = self.main_menu.handle_click(pos)
            if act == "start":
                self._start_play()
            elif act == "settings":
                self._open_settings()
            elif act == "exit":
                save_settings(self.settings)
                self.running = False
            return

        if self.scene == AppScene.SETTINGS and self.settings_scene:
            res = self.settings_scene.handle_mouse_down(pos, button)
            if res == "back":
                save_settings(self.settings)
                self.settings_scene = None
                self.scene = AppScene.MAIN_MENU
                game_logging.log_state("Cena: MAIN_MENU (definições)")
            return

        if self.scene == AppScene.PLAYING and self.play_state:
            st = self.play_state
            if st.level_up_paused:
                idx = self.ui.upgrade_menu.click_at(pos)
                if idx is not None:
                    st.select_upgrade(idx)
            return

        if self.scene == AppScene.GAME_OVER and self.play_state:
            r0, r1 = self.ui.death_restart_rect, self.ui.death_menu_rect
            if r0 and r0.collidepoint(pos):
                self.play_state.reset_run(keep_meta=True)
                self.scene = AppScene.PLAYING
                game_logging.log_state("Cena: PLAYING (recomeçar)")
            elif r1 and r1.collidepoint(pos):
                self.saved_prestige_points = self.play_state.prestige_points
                self.play_state = None
                self.scene = AppScene.MAIN_MENU
                game_logging.log_state("Cena: MAIN_MENU (game over)")

    def update(self, dt: float) -> None:
        if self.scene == AppScene.MAIN_MENU:
            self.main_menu.update(dt)
        elif self.scene == AppScene.PLAYING and self.play_state:
            st = self.play_state
            if not st.game_paused:
                keys = pygame.key.get_pressed()
                dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (
                    keys[pygame.K_a] or keys[pygame.K_LEFT]
                )
                dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (
                    keys[pygame.K_w] or keys[pygame.K_UP]
                )
                st.move_player(dx, dy, dt)
            st.update(dt)
            if st.death_mode == "await_click":
                self.scene = AppScene.GAME_OVER
                game_logging.log_state("Cena: GAME_OVER")

    def draw(self) -> None:
        if self.scene == AppScene.MAIN_MENU:
            self.main_menu.draw(self.screen)
        elif self.scene == AppScene.SETTINGS and self.settings_scene:
            self.settings_scene.draw(self.screen)
        elif self.scene in (AppScene.PLAYING, AppScene.GAME_OVER) and self.play_state:
            self.ui.draw_frame(self.screen, self.play_state)
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            mx, my = pygame.mouse.get_pos()
            if (
                self.scene == AppScene.PLAYING
                and self.play_state
                and self.play_state.level_up_paused
            ):
                self.ui.handle_upgrade_hover((mx, my), self.play_state)

            self.handle_events()
            self.update(dt)
            self.draw()

        try:
            self.audio.stop_music()
        except Exception:
            pass
        pygame.quit()
