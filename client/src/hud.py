import pygame

from assets import Assets


class Hud:
    def __init__(self, client, screen_size):
        self.client = client
        self.screen_size = screen_size
        self.heart_image = pygame.image.load(Assets.get("hud", "ui_heart_full.png")).convert_alpha()
        self.half_heart_image = pygame.image.load(Assets.get("hud", "ui_heart_half.png")).convert_alpha()
        self.empty_heart_image = pygame.image.load(Assets.get("hud", "ui_heart_empty.png")).convert_alpha()

    def render(self, camera):
        if self.client.player:
            for i in range(0, self.client.player.max_health // 10):
                if self.client.player.health >= (i + 1) * 10:
                    camera.renderTexture.blit(self.heart_image, (5 + 15 * i, 5))
                elif self.client.player.health >= i * 10 + 5:
                    camera.renderTexture.blit(self.half_heart_image, (5 + 15 * i, 5))
                else:
                    camera.renderTexture.blit(self.empty_heart_image, (5 + 15 * i, 5))
