# This file contains the camera. The camera is mainly a data structure storing an offset that can be applied while
# rendering. The camera also offers features to track a target, scale the rendered texture or add screen shake.

import random

import pygame

from player import ClientEntity
from common.src.vec.Vec2i import Vec2i


class Camera:
    # camera modes
    FREE = 0
    FOLLOW_TARGET = 1

    def __init__(self, screen_size: pygame.Vector2, virtual_screen_size_scaler: int,
                 position: Vec2i = Vec2i(), display_flags=0, vsync=0):
        self.position = position
        self.display = pygame.display.set_mode(screen_size, display_flags, vsync=vsync)
        pygame.display.set_caption("Tombstone Tunnels")
        self.renderTexture = pygame.Surface((
            int(screen_size.x / virtual_screen_size_scaler + 1),
            int(screen_size.y / virtual_screen_size_scaler + 1)
        ))
        self.zoom = 1
        self.screen_shake = False  # apply a random screen shake effect every
        self.target: ClientEntity = None  # entity with .position member var (entity that the camera will follow)
        self.tracking_speed = .999
        self.mode = self.FREE

    def update(self, delta_time, debugger=None):
        self.draw(debugger)
        self.update_position(delta_time)

    def update_position(self, delta_time):
        if not self.target:
            return
        if self.mode == self.FREE:
            pass
        elif self.mode == self.FOLLOW_TARGET:
            self.position.x += (self.target.animated_position.x - self.position.x - self.renderTexture.get_width() / 2) * self.tracking_speed * delta_time
            self.position.y += (self.target.animated_position.y - self.position.y - self.renderTexture.get_height() / 2) * self.tracking_speed * delta_time

    def draw(self, debugger=None):
        dpx = self.display.get_size()[0]
        dpy = self.display.get_size()[1]

        if self.screen_shake:  # Increase zoom to a minimum of 1.1 to avoid black borders when applying screen shake
            self.zoom = max(self.zoom, 1.1)

        self.display.blit(
            pygame.transform.scale(
                self.renderTexture,
                (int(dpx * self.zoom), int(dpy * self.zoom)),
            ),
            (
                - int(.5 * (dpx * self.zoom - dpx)) + self.screen_shake * (random.randint(-4, 4)),
                - int(.5 * (dpy * self.zoom - dpy)) + self.screen_shake * (random.randint(-4, 4))
            )
        )

        if debugger:
            debugger.renderDebug()
        pygame.display.flip()
        self.renderTexture.fill((0, 0, 0))
        self.display.fill((255, 0, 0))

    def world_to_screen(self, point: pygame.Vector2):
        """Converts a point from world coordinates to screen coordinates"""
        return point - self.position

    def screen_to_world(self, point: pygame.Vector2):
        """Converts a point from screen coordinates to world coordinates"""
        return point + self.position
