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
    CAMERA_SPEED = 0.8

    def __init__(self, client):
        self.client = client

        # window
        self.monitor_size = pygame.Vector2(pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.window_size = self.monitor_size / 2
        self.window_flags = pygame.HWACCEL | pygame.HWSURFACE | pygame.DOUBLEBUF
        self.window_surface = pygame.display.set_mode(self.window_size, flags=self.window_flags)
        self.draw_surface = pygame.Surface(self.window_size*2)

        # ui
        self.main_screen = MainScreen(self, self.window_surface, self.window_size)
        self.connecting_screen = ConnectingScreen(self, self.window_surface, self.window_size)

        # camera
        self.camera_offset = pygame.Vector2(0, 0)
        self.camera_target = None

        # game
        self.tilemap = ClientTileMap(self, self.TILE_SIZE)
        self.debugger = Debugger()

    def _update_camera(self, events, dt):
        """Follow camera target, if it exists."""
        if self.camera_target:
            self.camera_offset.x += (self.camera_target.animated_position.x*8 - self.camera_offset.x - self.window_size.x / 2) * self.CAMERA_SPEED * dt
            self.camera_offset.y += (self.camera_target.animated_position.y*8 - self.camera_offset.y - self.window_size.y / 2) * self.CAMERA_SPEED * dt

    def _update_ui(self, state, events, dt):
        if state == client_state.MAIN_MENU:
            self.main_screen.update(events, dt)
        elif state == client_state.CONNECTING:
            self.connecting_screen.update(events, dt)

    def _render_ui(self, state):
        if state == client_state.MAIN_MENU:
            self.main_screen.render()
        elif state == client_state.CONNECTING:
            self.connecting_screen.render()
        pygame.display.update()

    def _render_game(self, dt):
        # tile map
        self.tilemap.render(self.draw_surface)

        # entities (main surface)
        from player import ClientEntity
        entity: ClientEntity
        for entity in self.client.get_all_entities():
            if entity:
                entity.render(self.draw_surface)

        # debug text
        self.debugger.debug(f"dt: {int(dt*1000)}ms")
        if dt != 0:
            self.debugger.debug(f"FPS: {int(1 / dt)}")
        else:
            self.debugger.debug("FPS: ∞")

        # draw to window
        self.window_surface.blit(self.draw_surface, -self.camera_offset)
        self.debugger.render(self.window_surface)
        pygame.display.update()

        self.draw_surface.fill((0, 0, 0))
        self.window_surface.fill((0, 0, 0))

    def update(self, state, events, dt):
        """Update the game. This doesn't render anything, but e.g. moves the camera or updates the ui."""
        if self.client.state == client_state.IN_GAME:
            self._update_camera(events, dt)
        else:
            self._update_ui(state, events, dt)

    def render(self, state, dt):
        """Render the game. This should not carry out any (game) logic, only rendering."""
        if self.client.state == client_state.IN_GAME:
            self._render_game(dt)
        else:
            self._render_ui(state)

    def toggle_fullscreen(self):
        """Toggles fullscreen mode."""
        if pygame.display.is_fullscreen():
            # we are in fullscreen mode
            pygame.display.toggle_fullscreen()
            self.window_size = self.monitor_size / 2
            self.window_surface = pygame.display.set_mode(self.window_size, flags=self.window_flags)
            self.draw_surface = pygame.Surface(self.window_size)
        else:
            # we are in windowed mode
            self.window_size = self.monitor_size
            self.window_surface = pygame.display.set_mode(self.window_size, flags=self.window_flags)
            self.draw_surface = pygame.Surface(self.window_size)
            pygame.display.toggle_fullscreen()
