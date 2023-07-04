"""
This file contains the camera. The camera is mainly a data structure storing an offset that can be applied while
rendering. The camera also offers features to track a target, scale the rendered texture or add screen shake.
"""

import random

import pygame
from pygame import Vector2

from entities import ClientEntity


class Camera:
    # camera modes. FREE means the camera is not tracking any entity. FOLLOW_TARGET means the camera is tracking
    # the target entity
    FREE = 0
    FOLLOW_TARGET = 1

    def __init__(self, renderer, screen_size: Vector2, virtual_screen_size_scaler: int,
                 position: Vector2 = Vector2(), display_flags=0, vsync=0):
        self.renderer = renderer  # renderer instance
        self.position = position  # camera position
        self.display = pygame.display.set_mode(screen_size, display_flags, vsync=vsync)  # display surface
        pygame.display.set_caption("Tombstone Tunnels")  # set window title
        self.renderTexture = pygame.Surface((
            int(screen_size.x / virtual_screen_size_scaler + 1),
            int(screen_size.y / virtual_screen_size_scaler + 1)
        ))
        self.zoom = 1  # zoom factor
        self.screen_shake = False  # apply a random screen shake effect every
        self.target: ClientEntity | None = None  # entity with .position member var (entity that the camera will follow)
        self.tracking_speed = .999   # tracking speed (0-1) (1 = instant tracking) (0 = no tracking)
        self.mode = self.FREE  # camera mode (FREE or FOLLOW_TARGET; see above)

    def update(self, delta_time, debugger=None):
        """
        Updates the camera position and draws the render texture to the display surface.
        """
        self.draw(debugger)
        self.update_position(delta_time)

    def update_position(self, delta_time):
        """
        Updates the camera position based on the current mode and target.
        Additionally, a tracking speed is applied to make the camera follow the target smoothly.
        """
        if not self.target:
            # no target, nothing to do
            return
        if self.mode == self.FREE:
            # don't move the camera, we are in free mode
            pass
        elif self.mode == self.FOLLOW_TARGET:
            # move the camera towards the target
            self.position.x += (self.target.animated_position.x - self.position.x - self.renderTexture.get_width() / 2) * self.tracking_speed * delta_time
            self.position.y += (self.target.animated_position.y - self.position.y - self.renderTexture.get_height() / 2) * self.tracking_speed * delta_time

    def draw(self, debugger=None):
        """
        Draws the render texture to the display surface. If a debugger is passed, it will be drawn on top of the render
        texture. The render texture is then cleared. This method also applies screen shake if the camera is shaking.
        """
        dpx = self.display.get_size()[0]
        dpy = self.display.get_size()[1]
        self.screen_shake = False  # disable screen shake for now
        if self.renderer.client.player:
            # self.screen_shake = self.renderer.client.player.health <= 10
            pass

        if self.screen_shake:  # Increase zoom to a minimum of 1.1 to avoid black borders when applying screen shake
            self.zoom = max(self.zoom, 1.1)

        # Draw the texture to the display surface. To simulate the camera, apply the current offset.
        # Additionally, when camera shake is enabled, apply an extra random offset to the texture.
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

        # When the user enabled debugging by pressing F3, draw some debug text on top of the render texture
        if debugger:
            debugger.renderDebug()
        # Call flip() on the display surface to make the changes visible
        pygame.display.flip()
        # Fill the render texture to clear it for the next frame
        self.renderTexture.fill((0, 0, 0))
        self.display.fill((255, 0, 0))

    def world_to_screen(self, point: pygame.Vector2):
        """Converts a point from world coordinates to screen coordinates"""
        return point - self.position

    def screen_to_world(self, point: pygame.Vector2):
        """Converts a point from screen coordinates to world coordinates"""
        return point + self.position

    @staticmethod
    def toggle_fullscreen():
        """Toggles fullscreen mode"""
        pygame.display.toggle_fullscreen()
