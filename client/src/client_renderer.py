import os

from camera import *
from debug import *
from tilemap import TileMap
from ui import UI

PATHTOTILEIMAGES = os.path.join(os.path.dirname(__file__), "..", "assets", "tilemap", "tiles")
PATHTOTESTMAP = os.path.join(os.path.dirname(__file__), "..", "assets", "tilemap", "maps", "testmap.csv")


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
        self.ui = UI(self, self.camera.display, screen_size)
        self.debugger = Debugger()

    def _tick_ui(self, events, dt):
        self.ui.tick(events, dt)
        pygame.display.update()

    def _tick_game(self, events, dt):
        self.tilemap.render(self.camera)

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

    def tick(self, events, dt):
        if self.client.state == self.client.MAIN_MENU:
            self._tick_ui(events, dt)
        elif self.client.state == self.client.IN_GAME:
            self._tick_game(events, dt)
