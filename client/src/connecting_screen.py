"""
File for managing the connection screen.
"""

import pygame
import pygame_gui


class ConnectingScreen:
    """
    Class containing the logic and ui elements for the connecting screen.
    """
    def __init__(self, renderer, window_surface, screen_size):
        self.renderer = renderer  # renderer instance
        self.window_surface = window_surface  # pygame window surface
        self.manager = pygame_gui.UIManager(screen_size)  # pygame gui window manager
        # rectangle defining the position and size of the info text
        info_text_rect = pygame.Rect(
            (screen_size[0] / 2 - screen_size[0] / 10, screen_size[1] / 2 - screen_size[1] / 10),
            (screen_size[0] / 5, screen_size[1] / 5)
        )
        self.ui_background = pygame.Surface(screen_size)
        # info text
        self.info_text = pygame_gui.elements.UITextBox(relative_rect=info_text_rect,
                                                       html_text="<strong>Connecting...</strong>",
                                                       manager=self.manager)

    def tick(self, events, dt):
        """
        Method called every tick to update the connecting screen. This method is called by the renderer.
        :param events: list of pygame events
        :param dt: delta time
        """
        for event in events:
            self.manager.process_events(event)

        self.manager.update(dt)

        self.window_surface.blit(self.ui_background, (0, 0))
        self.manager.draw_ui(self.window_surface)
