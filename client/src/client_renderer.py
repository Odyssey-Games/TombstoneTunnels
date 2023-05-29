# This class stores some of the essential game objects like the Tilemap, camera and screen objects. It also
# contains the main loop functions for the game and menus

import client_state
from camera import *
from client_tiles import ClientTileMap
from connecting_screen import ConnectingScreen
from debug import *
from main_screen import MainScreen

TILE_SIZE = 16  # declaring this twice because of circular imports


class ClientRenderer:
    def __init__(self, client):
        self.client = client
        self.ofx = 0
        self.ofx = 0
        self.dt = 0
        # set camera before tilemap (pygame image mode has to be set for loading images in tilemap)
        monitor_info = pygame.display.Info()
        self.screen_size = pygame.Vector2(1280, 720)
        self.texture_size = pygame.Vector2(200, 200)
        self.camera = Camera(
            screen_size=self.screen_size,  # todo dynamic screen size
            texture_size=self.texture_size,
            offset=pygame.Vector2(0, 0),
            # does pygame.HWACCEL make a difference?
            display_flags=pygame.HWACCEL,
        )
        self.tilemap = ClientTileMap(self, TILE_SIZE)
        self.camera.mode = self.camera.FOLLOW_TARGET
        self.main_screen = MainScreen(self, self.camera.display, self.screen_size)
        self.connecting_screen = ConnectingScreen(self, self.camera.display, self.screen_size)
        self.debugger = Debugger()
        self.pressed_keys = set()

    def _tick_ui(self, state, events, dt):
        if state == client_state.MAIN_MENU:
            self.main_screen.tick(events, dt)
        elif state == client_state.CONNECTING:
            self.connecting_screen.tick(events, dt)
        pygame.display.update()

    def _tick_game(self, events, dt):
        # handle key events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.camera.zoom += .1
                elif event.key == pygame.K_e:
                    self.camera.zoom = max(self.camera.zoom - .1, 1)
                elif event.key == pygame.K_l:
                    self.camera.position.x += 10
                elif event.key == pygame.K_j:
                    self.camera.position.x -= 10
                elif event.key == pygame.K_SPACE:
                    self.camera.screen_shake = not self.camera.screen_shake

        # render tilemap
        self.tilemap.render(self.camera)
        # render player
        if self.client.player:
            self.client.player.render(self.camera)
            self.debugger.debug(f"Player pos: {self.client.player.tile_position}")

        # render other entities
        for entity in self.client.entities:
            entity.render(self.camera)

        self.debugger.debug(int(self.client.clock.get_fps()))

        self.camera.update(dt, self.debugger)

    def tick(self, state, events, dt):
        if self.client.state == client_state.IN_GAME:
            self._tick_game(events, dt)
        else:
            self._tick_ui(state, events, dt)
