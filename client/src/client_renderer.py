# This class stores some of the essential game objects like the Tilemap, camera and screen objects. It also
# contains the main loop functions for the game and menus

import client_state
from camera import *
from client_tiles import ClientTileMap
from connecting_screen import ConnectingScreen
from debug import *
from hud import Hud
from main_screen import MainScreen

TILE_SIZE = 16  # declaring this twice because of circular imports


class ClientRenderer:
    def __init__(self, client):
        self.client = client
        self.dt = 0
        # set camera before tilemap (pygame image mode has to be set for loading images in tilemap)
        screen_size = pygame.Vector2(960, 540)
        # Camera instance to manage camera movement, screen shake, etc.
        self.camera = Camera(
            self,
            screen_size=screen_size,
            virtual_screen_size_scaler=2,
            position=Vector2(0, 0),
            # does pygame.HWACCEL make a difference?
            display_flags=pygame.HWACCEL | pygame.SCALED,
        )
        # Tilemap instance to manage tilemap rendering
        self.tilemap = ClientTileMap(self.client, TILE_SIZE)
        # set camera mode to follow target so that it follows the player
        self.camera.mode = self.camera.FOLLOW_TARGET
        # MainScreen instance to manage the main menu
        self.main_screen = MainScreen(self, self.camera.display, screen_size)
        # ConnectingScreen instance to manage the connecting screen
        self.connecting_screen = ConnectingScreen(self, self.camera.display, screen_size)
        # Hud instance to manage the hud (heads up display)
        self.hud = Hud(self.client, screen_size)
        # Debugger instance to print extra debug information to the screen
        self.debugger = Debugger()
        # a set (unique values) where the currently pressed keys are updated every tick
        self.pressed_keys = set()

    def _tick_ui(self, state, events, dt):
        """
        Method called when not in game. Renders either the main menu or the connecting screen, depending on the state.
        :param state: either client_state.MAIN_MENU or client_state.CONNECTING
        :param events: list of pygame events
        :param dt: delta time
        """
        if state == client_state.MAIN_MENU:
            self.main_screen.tick(events, dt)
        elif state == client_state.CONNECTING:
            self.connecting_screen.tick(events, dt)
        pygame.display.update()

    def _tick_game(self, events, dt):
        """
        Method called when in game. Renders the tilemap, player, entities, etc.
        :param events: list of pygame events
        :param dt: delta time
        """
        # handle key events
        for event in events:
            if event.type == pygame.KEYDOWN:
                # if event.key == pygame.K_q:
                #     self.camera.zoom += .1
                # elif event.key == pygame.K_e:
                #     self.camera.zoom = max(self.camera.zoom - .1, 1)
                if event.key == pygame.K_l:
                    self.camera.position.x += 10
                elif event.key == pygame.K_j:
                    self.camera.position.x -= 10
                # elif event.key == pygame.K_SPACE:
                #     self.camera.screen_shake = not self.camera.screen_shake

        # render tilemap
        self.tilemap.render(self.camera)
        # render player
        if self.client.player:
            self.client.player.render(self.camera, dt)

        # render other entities
        for entity in self.client.entities:
            entity.render(self.camera, dt)

        # render hud
        self.hud.render(self.camera)

        # if debug is enabled print the current frame count to the screen
        self.debugger.debug(int(self.client.clock.get_fps()))

        self.camera.update(dt, self.debugger)

    def tick(self, state, events, dt):
        """
        Tick either the game or the ui depending on the state.
        :param state: client_state.MAIN_MENU, client_state.CONNECTING or client_state.IN_GAME
        :param events: list of pygame events
        :param dt: delta time
        """
        if self.client.state == client_state.IN_GAME:
            self._tick_game(events, dt)
        else:
            self._tick_ui(state, events, dt)
