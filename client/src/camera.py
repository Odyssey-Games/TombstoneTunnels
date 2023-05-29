# This file contains the camera. The camera is mainly a data structure storing an offset that can be applied while
# rendering. The camera also offers features to track a target, scale the rendered texture or add screen shake.

import pygame

from vec.AbsPos import AbsPos
from player import ClientEntity


class Camera:
    # camera modes
    FREE = 0
    FOLLOW_TARGET = 1

    SCALE_FACTOR = 8

    def __init__(self, screen_size: pygame.Vector2, texture_size: pygame.Vector2,
                 offset: pygame.Vector2 = pygame.Vector2(), display_flags=0, vsync=0):
        self.offset = offset
        self.screen_size = screen_size
        self.display_flags = display_flags
        self.vsync = vsync
        self.display = None
        self.update_display()
        self.texture_size = texture_size
        pygame.display.set_caption("Tombstone Tunnels")
        # Everything is rendered on the render_texture surface. This surface is then scaled and blitted to the display
        # surface with a specific offset to simulate a camera effect. That way, the camera can be moved around smoothly
        # while the rendering remains pixel-perfect (we don't need to upscale every single texture).
        self.render_texture = pygame.Surface(texture_size)
        self.zoom = 1
        self.screen_shake = False  # apply a random screen shake effect every
        self.target: ClientEntity | None = None  # entity with .position member var (entity that the camera will follow)
        self.tracking_speed = .8
        self.mode = self.FREE

    def update_display(self):
        self.display = pygame.display.set_mode(self.screen_size, self.display_flags, self.vsync)

    def update(self, delta_time, debugger=None):
        self.draw(debugger)
        self.update_position(delta_time)

    def update_position(self, delta_time):
        if self.mode == self.FOLLOW_TARGET and self.target:
            target_screen_pos = self.world_to_screen(self.target.animated_position) + pygame.Vector2(8 * 8, 8 * 8)
            target_vector = (target_screen_pos - self.screen_size / 2)
            self.offset.x += target_vector.x * self.tracking_speed * delta_time
            self.offset.y += target_vector.y * self.tracking_speed * delta_time

    def draw(self, debugger=None):
        dpx = self.display.get_size()[0]
        dpy = self.display.get_size()[1]

        if self.screen_shake:  # Increase zoom to a minimum of 1.1 to avoid black borders when applying screen shake
            self.zoom = max(self.zoom, 1.1)

        scaled_texture = pygame.transform.scale_by(
            self.render_texture,
            self.SCALE_FACTOR,
        )
        self.display.blit(
            scaled_texture,
            -self.offset
        )

        if debugger:
            debugger.renderDebug()
        pygame.display.flip()
        self.render_texture.fill((0, 0, 0))
        self.display.fill((0, 0, 0))

    def world_to_screen(self, point: AbsPos):
        """Converts a point from world coordinates to screen coordinates"""
        return pygame.Vector2(point.x * self.SCALE_FACTOR - self.offset.x, point.y * self.SCALE_FACTOR - self.offset.y)

    def toggle_fullscreen(self):
        # todo fix fullscreen res
        """Toggles fullscreen mode"""
        pygame.display.toggle_fullscreen()
