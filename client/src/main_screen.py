# This File contains the update function for the login screen

import pygame
import pygame_gui

import client_state
from assets import Assets
from common.src.common import VERSION


class MainScreen:
    def __init__(self, renderer, window_surface, screen_size):
        self.renderer = renderer  # ClientRenderer instance
        self.window_surface = window_surface

        # load theme and assets
        self.manager = pygame_gui.UIManager(screen_size, Assets.get("menu", "theme.json"))
        self.manager.add_font_paths("dungeon", Assets.get("fonts", "dungeon.ttf"))
        self.ui_background = pygame.image.load(Assets.get("menu", "background.png")).convert()
        self.logo = pygame.image.load(Assets.get("menu", "logo_big.png")).convert_alpha()

        # big logo image
        self.logo_image = pygame_gui.elements.UIImage(relative_rect=pygame.Rect((0, -100), (600, 300)),
                                                      image_surface=self.logo,
                                                      anchors={'center': 'center'},
                                                      )
        self.play_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 160), (450, 130)),
                                                        text='PLAY ONLINE',
                                                        manager=self.manager,
                                                        anchors={'center': 'center'},
                                                        object_id="#play_button")

        # text field for changing the player name
        self.name_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((0, 70), (450, 50)),
                                                              manager=self.manager,
                                                              anchors={'center': 'center'},
                                                              initial_text=self.renderer.client.config.player_name)

        # small version label showing the current TombstoneTunnels version
        self.version_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 0), (-1, -1)),
                                                         text=f' {VERSION}',
                                                         manager=self.manager)

        # custom server text entry + connect button
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

        # quit and fullscreen buttons
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
        """
        Called every frame. Update the UI and process ui-specific events.
        :param events: list of pygame events
        :param dt: delta time
        """
        for event in events:
            self.manager.process_events(event)
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.play_button:
                    # log in to public/default server
                    print('Logging in...')
                    self.renderer.client.state = client_state.CONNECTING
                    self.renderer.client.networking.try_login(False)
                elif event.ui_element == self.custom_server_button:
                    # log in to custom server
                    print('Logging in (custom)...')
                    self.renderer.client.state = client_state.CONNECTING
                    self.renderer.client.networking.try_login(True)
                elif event.ui_element == self.fullscreen_button:
                    # toggle fullscreen
                    print('Toggling fullscreen...')
                    pygame.display.toggle_fullscreen()
                elif event.ui_element == self.quit_button:
                    # quit
                    print('Quitting...')
                    self.renderer.client.running = False
            elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == self.name_entry:
                    # change player name
                    name = event.text[:20]
                    print('Changing name to', name)
                    self.name_entry.text = name
                    self.renderer.client.config.player_name = name
                elif event.ui_element == self.custom_server_edit:
                    # change custom server address
                    print('Changing custom server address to', event.text)
                    self.renderer.client.set_custom_address(event.text)

        # Tell the PyGame GUI manager to update itself; e.g. button animations, text entry caret blinking
        self.manager.update(dt)

        # Draw the PyGame GUI manager
        self.window_surface.blit(self.ui_background, (0, 0))  # background
        self.manager.draw_ui(self.window_surface)  # ui
