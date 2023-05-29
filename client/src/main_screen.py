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
        self.ui_background = pygame.image.load(Assets.get("menu", "background.png"))
        self.logo = pygame.image.load(Assets.get("menu", "logo_big.png"))

        self.logo_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((0, -100), (600, 300)),
                                                      image_surface=self.logo,
                                                      anchors={'center': 'center'},
                                                      )
        self.play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 160), (450, 130)),
                                                        text='PLAY ONLINE',
                                                        manager=self.manager,
                                                        anchors={'center': 'center'},
                                                        object_id="#play_button")

        self.name_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, 70), (450, 50)),
                                                              manager=self.manager,
                                                              anchors={'center': 'center'},
                                                              initial_text=self.renderer.client.config.player_name)

        self.version_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 0), (-1, -1)),
                                                         text=f' {VERSION}',
                                                         manager=self.manager)

        bottom_right = pygame.Rect(0, 0, 200, 50)
        bottom_right.bottomright = (0, 0)
        self.custom_server_button = pygame_gui.elements.UIButton(
            relative_rect=bottom_right,
            text='JOIN CUSTOM SERVER',
            manager=self.manager,
            anchors={'right': 'right', 'bottom': 'bottom'},
        )
        custom_addr = self.renderer.client.config.custom_server_address
        custom_server_text = f"{custom_addr[0]}:{custom_addr[1]}"
        if custom_addr[1] == self.renderer.client.networking.DEFAULT_SERVER_PORT:
            custom_server_text = custom_addr[0]
        self.custom_server_edit = pygame_gui.elements.UITextEntryLine(
            relative_rect=bottom_right,
            manager=self.manager,
            anchors={'right': 'right', 'bottom': 'bottom', 'bottom_target': self.custom_server_button},
            initial_text=custom_server_text
        )

        top_right = pygame.Rect(0, 0, 50, 50)
        top_right.topright = (0, 0)
        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=top_right,
            text='X',
            manager=self.manager,
            anchors={'right': 'right', 'top': 'top'},
            object_id="#quit_button"
        )
        self.fullscreen_button = pygame_gui.elements.UIButton(
            relative_rect=top_right,
            text='[]',
            manager=self.manager,
            anchors={'right': 'right', 'top': 'top', 'right_target': self.quit_button},
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
                elif event.ui_element == self.fullscreen_button:
                    print('Toggling fullscreen...')
                    self.renderer.camera.toggle_fullscreen()
                elif event.ui_element == self.quit_button:
                    print('Quitting...')
                    self.renderer.client.running = False
            elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == self.name_entry:
                    name = event.text[:20]
                    print('Changing name to', name)
                    self.name_entry.text = name
                    self.renderer.client.config.player_name = name
                elif event.ui_element == self.custom_server_edit:
                    print('Changing custom server address to', event.text)
                    self.renderer.client.set_custom_address(event.text)

        self.manager.update(dt)

        self.window_surface.blit(self.ui_background, (0, 0))
        self.manager.draw_ui(self.window_surface)
