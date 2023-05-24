# This File contains the update function for the login screen

import pygame
import pygame_gui
import client_state
from assets import Assets
from common.src.common import VERSION


class MainScreen:
    def __init__(self, renderer, window_surface, screen_size):
        self.renderer = renderer
        self.window_surface = window_surface

        self.manager = pygame_gui.UIManager(screen_size, Assets.get("menu", "theme.json"))
        self.manager.add_font_paths("dungeon", Assets.get("fonts", "dungeon.ttf"))
        self.ui_background = pygame.Surface(screen_size)
        self.play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0), (500, 200)),
                                                        text='PLAY ONLINE',
                                                        manager=self.manager,
                                                        anchors={'center': 'center'},
                                                        object_id="#play_button")

        self.version_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 0), (-1, -1)),
                                                         text=f' TT {VERSION}',
                                                         manager=self.manager)

        bottom_right = pygame.Rect(0, 0, 200, 50)
        bottom_right.bottomright = (0, 0)
        self.custom_server_button = pygame_gui.elements.UIButton(
            relative_rect=bottom_right,
            text='JOIN CUSTOM SERVER',
            manager=self.manager,
            anchors={'right': 'right', 'bottom': 'bottom'},
        )
        self.custom_server_edit = pygame_gui.elements.UITextEntryLine(
            relative_rect=bottom_right,
            manager=self.manager,
            anchors={'right': 'right', 'bottom': 'bottom', 'bottom_target': self.custom_server_button},
            initial_text="localhost",
        )

        top_right = pygame.Rect(0, 0, 50, 50)
        top_right.topright = (0, 0)
        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=top_right,
            text='X',
            manager=self.manager,
            anchors={'right': 'right', 'top': 'top'},
        )

    def tick(self, events, dt):
        for event in events:
            self.manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.play_button:
                    print('Logging in...')
                    self.renderer.client.state = client_state.CONNECTING
                    self.renderer.client.networking.try_login(False)
                elif event.ui_element == self.custom_server_button:
                    print('Logging in (custom)...')
                    self.renderer.client.state = client_state.CONNECTING
                    self.renderer.client.networking.try_login(True)
                elif event.ui_element == self.quit_button:
                    print('Quitting...')
                    self.renderer.client.running = False
            elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == self.custom_server_edit:
                    print('Changing custom server address to', event.text)
                    self.renderer.client.networking.set_custom_address(event.text)

        self.manager.update(dt)

        self.window_surface.blit(self.ui_background, (0, 0))
        self.manager.draw_ui(self.window_surface)
