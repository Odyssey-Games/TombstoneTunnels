import pygame
import pygame_gui
import client_state


class MainScreen:
    def __init__(self, renderer, window_surface, screen_size):
        self.renderer = renderer
        self.window_surface = window_surface
        self.manager = pygame_gui.UIManager(screen_size)
        server_dropdown_rect = pygame.Rect(
            (screen_size[0] / 2 - screen_size[0] / 10, screen_size[1] / 2 - screen_size[1] / 5 - 20),
            (screen_size[0] / 5, screen_size[1] / 5)
        )
        self.ui_background = pygame.Surface(screen_size)
        self.server_dropdown = pygame_gui.elements.UIDropDownMenu(relative_rect=server_dropdown_rect,
                                                                  options_list=['localhost', 'odysseygames.de'],
                                                                  starting_option='localhost',
                                                                  manager=self.manager)
        connect_button_rect = pygame.Rect(
            (screen_size[0] / 2 - screen_size[0] / 10, screen_size[1] / 2 + 20),
            (screen_size[0] / 5, screen_size[1] / 5)
        )
        self.hello_button = pygame_gui.elements.UIButton(relative_rect=connect_button_rect,
                                                         text='Join',
                                                         manager=self.manager)

    def tick(self, events, dt):
        for event in events:
            self.manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.hello_button:
                    print('Logging in...')
                    self.renderer.client.state = client_state.CONNECTING
                    self.renderer.client.networking.try_login()
            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.server_dropdown:
                    print('Changing server address to', event.text)
                    self.renderer.client.networking.set_ip(event.text)

        self.manager.update(dt)

        self.window_surface.blit(self.ui_background, (0, 0))
        self.manager.draw_ui(self.window_surface)
