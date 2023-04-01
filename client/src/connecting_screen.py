import pygame
import pygame_gui


class ConnectingScreen:
    def __init__(self, renderer, window_surface, screen_size):
        self.renderer = renderer
        self.window_surface = window_surface
        self.manager = pygame_gui.UIManager(screen_size)
        info_text_rect = pygame.Rect(
            (screen_size[0] / 2 - screen_size[0] / 10, screen_size[1] / 2 - screen_size[1] / 10),
            (screen_size[0] / 5, screen_size[1] / 5)
        )
        self.ui_background = pygame.Surface(screen_size)
        self.info_text = pygame_gui.elements.UITextBox(relative_rect=info_text_rect,
                                                       html_text="<strong>Connecting...</strong>",
                                                       manager=self.manager)

    def tick(self, events, dt):
        for event in events:
            self.manager.process_events(event)

        self.manager.update(dt)

        self.window_surface.blit(self.ui_background, (0, 0))
        self.manager.draw_ui(self.window_surface)
