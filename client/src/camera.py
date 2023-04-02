# This file contains the camera. The camera is mainly a data structue storing an offset that can be applied while rendering.
# The camera also offers features to track a target, scale the rendertexture or add screenshake.

import random

import pygame


class Camera:
    # camera modes
    FREE = 0
    FOLLOW_TARGET = 1

    def __init__(self, screenSize: pygame.Vector2, virtualScrSizeScaler: int,
                 position: pygame.Vector2 = pygame.Vector2(0, 0), display_flags=0, vsync=0):
        self.position = position
        self.display = pygame.display.set_mode(screenSize, display_flags, vsync=vsync)
        pygame.display.set_caption("Tombstone Tunnels")
        self.renderTexture = pygame.Surface((int(screenSize.x / virtualScrSizeScaler + 1), int(screenSize.y / virtualScrSizeScaler + 1)))
        self.zoom = 1
        self.screenshake = False
        self.target = None  # entity with .position member var
        self.trackingSpeed = .999
        self.mode = self.FREE

    def update(self, deltaTime, debugger=None):
        self.draw(debugger)
        self.updatePosition(deltaTime)

    def updatePosition(self, deltaTime):
        if not self.target:
            return
        if self.mode == self.FREE:
            pass
        elif self.mode == self.FOLLOW_TARGET:
            self.position.x += (self.target.position.x - self.position.x - self.renderTexture.get_width() / 2) * self.trackingSpeed * deltaTime
            self.position.y += (self.target.position.y - self.position.y - self.renderTexture.get_height() / 2) * self.trackingSpeed * deltaTime

    def draw(self, debugger=None):
        dpx = self.display.get_size()[0]
        dpy = self.display.get_size()[1]

        if self.screenshake:
            self.zoom = max(self.zoom, 1.1)

        self.display.blit(
            pygame.transform.scale(
                self.renderTexture,
                (
                    int(dpx * self.zoom),
                    int(dpy * self.zoom)
                ),
            ),
            (
                # - ((.5 * self.renderTexture.get_width()*self.zoom) - (.5 * dpx)),
                - int(.5 * (dpx * self.zoom - dpx)) + self.screenshake * (random.randint(-4, 4)),
                - int(.5 * (dpy * self.zoom - dpy)) + self.screenshake * (random.randint(-4, 4))
            )
        )

        if debugger:
            debugger.renderDebug()
        pygame.display.flip()
        self.renderTexture.fill((0, 0, 0))
        self.display.fill((255, 0, 0))

    def worldToScr(self, point: pygame.Vector2):
        return point - self.position

    def scrToWorld(self, point: pygame.Vector2):
        return point + self.position
