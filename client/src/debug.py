# This file contains a class that allow you to render debug text on the screen

import pygame


class Debugger:
    def __init__(self):
        self.pos = (5, 5)
        self.content = []
        self.font = pygame.font.SysFont('Comic Sans MS', 24)
        self.enabled = False

    def debug(self, info):
        self.content.append(str(info))

    def render(self, surf):
        if not self.enabled:
            return

        for index, item in enumerate(self.content):
            text = self.font.render(item, 2, (200, 200, 200))
            pygame.draw.rect(surf, (0, 0, 0), pygame.Rect((4, index * text.get_height()),
                                                          (text.get_width(), text.get_height())))
            surf.blit(text, (4, index * text.get_height()))
        self.content = []
