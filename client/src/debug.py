# This file contains a class that allow you to render debug text on the screen

import pygame


class Debugger:
    def __init__(self):
        self.pos = (5, 5)  # small offset from top left of screen
        self.content = []  # list of debug content
        self.font = pygame.font.SysFont('Comic Sans MS', 24)  # pygame font
        self.enabled = False  # enabled state; can be toggled with F3

    def debug(self, info):
        """
        Append the info to the content list for this tick.
        :param info: the information; can be any type and will be converted to a string
        """
        self.content.append(str(info))

    def renderDebug(self):
        """
        If debug is enabled (user pressed F3) render the content list to the screen.
        """
        if not self.enabled:
            return  # debug is disabled

        surf = pygame.display.get_surface()
        for index, item in enumerate(self.content):
            itemText = self.font.render(item, 2, (200, 200, 200))
            # draw a rect for every text
            pygame.draw.rect(surf, (0, 0, 0), pygame.Rect((4, index * itemText.get_height()),
                                                          (itemText.get_width(), itemText.get_height())))
            surf.blit(itemText, (4, index * itemText.get_height()))
        self.content = []  # clear the content for the next tick
