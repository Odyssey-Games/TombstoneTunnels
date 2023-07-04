# Main entry point of the program
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..', '..'))  # fix common imports

import json
from pathlib import Path

import client_state
from camera import *
from config import ClientConfig
from client_networking import ClientNetworking
from client_renderer import ClientRenderer
from common.src.map.map import Map
from entities import ClientEntity


class Client:
    def __init__(self):
        pygame.init()  # we need to call init() before we can use pygame fonts for rendering
        self.clock = pygame.time.Clock()  # used for getting the delta time each frame
        self.networking = ClientNetworking(self)  # networking instance for sending and receiving packets
        self.config: ClientConfig = self._get_config()  # configuration of the client, loaded from config.json
        self.renderer = ClientRenderer(self)  # renderer instance for handling rendering
        self.map: Map | None = None  # the map we're currently on
        self.running = True  # whether the client game is running or not
        self.player = None  # gets assigned when we "get" our player from the server
        self.player_uuid = None  # gets assigned when we "get" our player from the server; unique identifier of the player
        self.entities: list[ClientEntity] = []  # other entities, can also be other players
        # State of the client. See client_state.py for more info.
        self.state = client_state.MAIN_MENU  # the current state of the client; see client_state.py for more info

    @staticmethod
    def get_config_file():
        """
        Gets the path of the config.json file. On Windows this is %localappdata%/TombstoneTunnels/config.json, on
        Linux this is ~/.TombstoneTunnels/config.json. MacOS is not supported yet.
        :return: The path to the config.json file, depending on the operating system.
        """
        config_dir = os.getenv("localappdata")
        if not config_dir or not os.path.exists(config_dir):  # we're probably on linux - todo macos support?
            print(Path.home())
            config_dir = os.path.join(Path.home(), ".TombstoneTunnels")
        else:
            # we're on windows
            config_dir = os.path.join(config_dir, "TombstoneTunnels")
        if not os.path.exists(config_dir):
            # create the config directory if it doesn't exist
            os.makedirs(config_dir)
        return os.path.join(config_dir, "config.json")

    @staticmethod
    def _get_config():
        """
        Load the client config from config.json.
        We use json to load the config and convert it to a ClientConfig object.
        """
        config_file = Client.get_config_file()
        try:
            with open(config_file) as f:
                # load as ClientConfig object
                return json.load(f, object_hook=lambda d: ClientConfig(**d))  # tells json we want a ClientConfig object
        except FileNotFoundError:
            # config.json not found, create default config
            print("config.json not found. Creating default config...")
            config = ClientConfig()
            with open(config_file, "w") as f:
                # write default values to the config file
                json.dump(config.__dict__, f, indent=4)
            return config

    def save_config(self):
        """Save the current client config to config.json."""
        config_file = Client.get_config_file()
        with open(config_file, "w") as f:
            # __dict__ is a dict containing all attributes of the object
            json.dump(self.config.__dict__, f, indent=4)

    def set_custom_address(self, address: str):
        """Sets the address of the custom server to connect to."""
        split = address.split(":")
        if len(split) == 1:
            # we have no port; use default port
            port = self.networking.DEFAULT_SERVER_PORT
        else:
            # user entered a port
            port = split[1]

        try:
            self.config.custom_server_address = (split[0], int(port))
        except ValueError:
            pass

    def _disconnect(self):
        """Reset variables. Note that networking.disconnect() has to be called separately (when necessary)."""
        self.state = client_state.MAIN_MENU
        self.player = None
        self.player_uuid = None
        self.entities.clear()

    def run(self):
        while self.running:
            # Main loop
            dt = self.clock.tick() / 1000
            events = [event for event in pygame.event.get()]
            if self.state == client_state.IN_GAME or self.state == client_state.CONNECTING:
                if not self.networking.tick(events, dt):  # networking.tick() returns false on disconnect
                    # disconnected from server; go to main menu
                    print("Disconnected from server.")
                    self._disconnect()
            # tick the renderer and the client
            self.tick(events, dt)
            self.renderer.tick(self.state, events, dt)

    def tick(self, events, dt):
        """
        Called every frame. Calls the update() functions on the player and entities, and handles events.
        """
        for event in events:
            if event.type == pygame.QUIT:
                # quit the game
                print("Exiting...")
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # toggle fullscreen
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_F3:
                    # toggle debugger
                    self.renderer.debugger.enabled = not self.renderer.debugger.enabled
                elif event.key == pygame.K_ESCAPE:
                    # escape key pressed; either disconnect from server or exit the game
                    if self.state == client_state.MAIN_MENU:
                        print("Exiting...")
                        self.running = False
                    else:
                        print("Disconnecting from server...")
                        self.networking.disconnect()
                        self._disconnect()

        if self.player:
            # update the player
            self.player.update(dt, self.renderer.tilemap, events)

        for entity in (self.entities + [self.player]):
            if entity:
                # tick all entities
                entity.tick(dt, events)

    def update_player(self, player):
        """Set our player and advise the camera to target the player."""
        self.player = player
        self.renderer.camera.target = player


if __name__ == "__main__":
    """
    Main entry point of the program. This is where we create the client instance and run it.
    """
    client = Client()
    try:
        client.run()
    except KeyboardInterrupt:
        # just exit the program when the user presses ctrl+c; no need to print an error message
        pass
    client.save_config()  # save the config when the client exits
    print("Saved config.")
