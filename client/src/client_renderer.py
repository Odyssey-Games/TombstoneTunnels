from time import time

import pygame

import client_state
from client_tiles import ClientTileMap
from connecting_screen import ConnectingScreen
from debug import Debugger
from main_screen import MainScreen


class ClientRenderer:
    """Client side renderer class for rendering the game."""
    TILE_SIZE = 16  # declaring this twice because of circular imports
    SCALE_FACTOR = 8

    def __init__(self, client):
        self.client = client

        # window
        self.monitor_size = pygame.Vector2(pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.window_size = self.monitor_size / 2
        self.window_flags = pygame.HWACCEL | pygame.HWSURFACE | pygame.DOUBLEBUF
        self.window_surface = pygame.display.set_mode(self.window_size, flags=self.window_flags)

        # ui
        self.main_screen = MainScreen(self, self.window_surface, self.window_size)
        self.connecting_screen = ConnectingScreen(self, self.window_surface, self.window_size)

        # camera
        self.camera_offset = pygame.Vector2(0, 0)
        self.camera_target = None

        # game
        self.tilemap_surface = pygame.Surface((self.TILE_SIZE * 16, self.TILE_SIZE * 16))
        self.tilemap = ClientTileMap(self, self.TILE_SIZE)
        self.main_surface = self.tilemap_surface.copy()
        self.debugger = Debugger()

    def _render_ui(self, state, events, dt):
        if state == client_state.MAIN_MENU:
            self.main_screen.tick(events, dt)
        elif state == client_state.CONNECTING:
            self.connecting_screen.tick(events, dt)
        pygame.display.update()

    def _render_game(self, dt):
        # tile map
        self.tilemap.render()

        # entities (main surface)
        for entity in self.client.get_all_entities():
            if entity:
                entity.render(self.main_surface)

        dest_surface = self.tilemap_surface.copy()
        scaled_main_surface = pygame.transform.scale_by(self.main_surface, self.SCALE_FACTOR)
        dest_surface.blit(scaled_main_surface.convert_alpha(), (0, 0))
        self.window_surface.blit(dest_surface, -self.camera_offset)

        # debug text
        if dt != 0:
            self.debugger.debug(f"FPS: {int(1 / dt)}")
        self.debugger.render(self.window_surface)

        pygame.display.flip()
        self.window_surface.fill((0, 0, 0))
        self.main_surface.fill((0, 0, 0))

    def render(self, state, events, dt):
        """Render the game. This should not carry out any (game) logic, only rendering."""
        if self.client.state == client_state.IN_GAME:
            self._render_game(dt)
        else:
            self._render_ui(state, events, dt)

    def toggle_fullscreen(self):
        """Toggles fullscreen mode."""
        if pygame.display.is_fullscreen():
            # we are in fullscreen mode
            pygame.display.toggle_fullscreen()
            self.window_size = self.monitor_size / 2
            self.window_surface = pygame.display.set_mode(self.window_size, flags=self.window_flags)
        else:
            # we are in windowed mode
            self.window_size = self.monitor_size
            self.window_surface = pygame.display.set_mode(self.window_size, flags=self.window_flags)
            pygame.display.toggle_fullscreen()
