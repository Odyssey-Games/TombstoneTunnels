# This class stores some of the essential game objects like the Tilemap, camera and screen objects. It also
# contains the main loop functions for the game and menus

import os

import client_state
from camera import *
from connecting_screen import ConnectingScreen
from debug import *
from main_screen import MainScreen
from tilemap import TileMap

if os.path.exists(os.path.join(os.path.dirname(__file__), "assets")):  # for pyinstaller; different assets folder loc
    PATH_TO_ASSETS = os.path.join(os.path.dirname(__file__), "assets")
else:
    PATH_TO_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
PATHTOTILEIMAGES = os.path.join(PATH_TO_ASSETS, "tilemap", "tiles")
PATHTOTESTMAP = os.path.join(PATH_TO_ASSETS, "tilemap", "maps", "testmap.csv")
TILE_SIZE = 16  # declaring this twice because of circular imports


class ClientRenderer:
    def __init__(self, client):
        self.client = client
        self.ofx = 0
        self.ofx = 0
        self.dt = 0
        # set camera before tilemap (pygame image mode has to be set for loading images in tilemap)
        screen_size = pygame.Vector2(1000, 600)
        self.camera = Camera(
            screen_size=screen_size,
            virtual_screen_size_scaler=4,
            position=pygame.Vector2(0, 0),
            # does pygame.HWACCEL make a difference?
            display_flags=pygame.HWACCEL | pygame.SCALED | pygame.RESIZABLE,
        )
        self.tilemap = TileMap(TILE_SIZE, PATHTOTILEIMAGES, PATHTOTESTMAP, pygame.Vector2(0, 0))
        self.camera.mode = self.camera.FOLLOW_TARGET
        self.main_screen = MainScreen(self, self.camera.display, screen_size)
        self.connecting_screen = ConnectingScreen(self, self.camera.display, screen_size)
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

        # render other entities
        for entity in self.client.entities:
            entity.render(self.camera)

        self.debugger.debug(f"entity count (without own player): {len(self.client.entities)}")
        self.debugger.debug(int(self.client.clock.get_fps()))

        self.camera.update(dt, self.debugger)

    def tick(self, state, events, dt):
        if self.client.state == client_state.IN_GAME:
            self._tick_game(events, dt)
        else:
            self._tick_ui(state, events, dt)
