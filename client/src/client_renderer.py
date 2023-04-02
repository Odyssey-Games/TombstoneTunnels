# This class stores some of the essential game objects like the Tilemap, camera and screen objects. It also 
# contains the main loop functions for the game and menus 

import os

from camera import *
from debug import *
from tilemap import TileMap
from main_screen import MainScreen
from connecting_screen import ConnectingScreen
import client_state

if os.path.exists(os.path.join(os.path.dirname(__file__), "assets")):
    PATH_TO_ASSETS = os.path.join(os.path.dirname(__file__), "assets")
else:
    PATH_TO_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
PATHTOTILEIMAGES = os.path.join(PATH_TO_ASSETS, "tilemap", "tiles")
PATHTOTESTMAP = os.path.join(PATH_TO_ASSETS, "tilemap", "maps", "testmap.csv")


class ClientRenderer:
    def __init__(self, client):
        self.client = client
        self.ofx = 0
        self.ofx = 0
        self.dt = 0
        # set camera before tilemap (pygame image mode has to be set for loading images in tilemap)
        screen_size = pygame.Vector2(1000, 600)
        self.camera = Camera(
            screenSize=screen_size,
            virtualScrSizeScaler=4,
            position=pygame.Vector2(0, 0),
            # does pygame.HWACCEL make a difference?
            display_flags=pygame.HWACCEL | pygame.SCALED,
        )
        self.tilemap = TileMap(16, PATHTOTILEIMAGES, PATHTOTESTMAP, pygame.Vector2(0, 0))
        self.camera.mode = self.camera.FOLLOW_TARGET
        self.main_screen = MainScreen(self, self.camera.display, screen_size)
        self.connecting_screen = ConnectingScreen(self, self.camera.display, screen_size)
        self.debugger = Debugger()

    def _tick_ui(self, state, events, dt):
        if state == client_state.MAIN_MENU:
            self.main_screen.tick(events, dt)
        elif state == client_state.CONNECTING:
            self.connecting_screen.tick(events, dt)
        pygame.display.update()

    def _tick_game(self, events, dt):

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.camera.zoom += .1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.camera.zoom = max(self.camera.zoom - .1, 1)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                self.camera.position.x += 10
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                self.camera.position.x -= 10
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.camera.screenshake = not self.camera.screenshake

        self.tilemap.render(self.camera)
        if self.client.player:
            self.client.player.render(self.camera)

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
