import pygame

from assets import Assets


class Hud:
    """
    Class for rendering the HUD (heads up display) elements on the client side. Currently, this renders the hearts
    depending on the health points of our player (10 health points are 1 heart; 5 health points are half a heart).
    """
    def __init__(self, client, screen_size):
        self.client = client
        self.screen_size = screen_size
        # full heart image
        self.heart_image = pygame.image.load(Assets.get("hud", "ui_heart_full.png")).convert_alpha()
        # half heart image
        self.half_heart_image = pygame.image.load(Assets.get("hud", "ui_heart_half.png")).convert_alpha()
        # empty heart image
        self.empty_heart_image = pygame.image.load(Assets.get("hud", "ui_heart_empty.png")).convert_alpha()

    def render(self, camera):
        """
        Render hearts depending on the player's health.
        :param camera: camera instance for accessing the render texture
        """
        if self.client.player:
            # player is initialized - // is int division
            for i in range(0, self.client.player.max_health // 10):
                if self.client.player.health >= (i + 1) * 10:
                    camera.renderTexture.blit(self.heart_image, (5 + 15 * i, 5))
                elif self.client.player.health >= i * 10 + 5:
                    camera.renderTexture.blit(self.half_heart_image, (5 + 15 * i, 5))
                else:
                    camera.renderTexture.blit(self.empty_heart_image, (5 + 15 * i, 5))
