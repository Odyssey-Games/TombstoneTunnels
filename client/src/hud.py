"""
File for Hud (in game overlay) rendering.
"""

import pygame
import pygame_gui


class Hud:
    def __init__(self, screen_size):
        self.manager = pygame_gui.UIManager((screen_size.x, screen_size.y))

        chat_rect = pygame.Rect((100, 100), (screen_size.x - 200, screen_size.y - 200))
        self.chat = pygame_gui.windows.UIConsoleWindow(chat_rect,
                                                       window_title="Chat",
                                                       visible=True,
                                                       manager=self.manager)

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self.chat.visible = True
            self.manager.process_events(event)
        self.chat.update(dt)
        self.manager.update(dt)

    def draw(self, surf):
        self.manager.draw_ui(surf)
