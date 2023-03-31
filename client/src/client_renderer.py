from tilemap import TileMap
from debug import *
from camera import *
import os

PATHTOTILEIMAGES = os.path.join(os.path.dirname(__file__), "..", "assets", "tilemap", "tiles")
PATHTOTESTMAP = os.path.join(os.path.dirname(__file__), "..", "assets", "tilemap", "maps", "testmap.csv")


class ClientRenderer:
    def __init__(self, client):
        self.client = client
        self.ofx = 0
        self.ofx = 0
        self.dt = 0
        # set camera before tilemap (pygame image mode has to be set for loading images in tilemap)
        self.camera = Camera(
            screenSize=pygame.Vector2(1000, 800),
            virtualScrSizeScaler=4,
            position=pygame.Vector2(0, 0)
        )
        self.tilemap = TileMap(16, PATHTOTILEIMAGES, PATHTOTESTMAP, pygame.Vector2(0, 0))
        self.camera.mode = self.camera.FOLLOWTARGET
        self.debugger = Debugger()

    def tick(self, events, dt):
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
