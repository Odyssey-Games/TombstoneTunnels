# Main entry point of the program
import json
import os
from pathlib import Path

import pygame

import client_state
from client_networking import ClientNetworking
from client_renderer import ClientRenderer
from common.src.map.map import Map
from config import ClientConfig
from player import ClientEntity


class Client:
    def __init__(self):
        pygame.init()  # we need to call init() before we can use pygame fonts for rendering
        self.clock = pygame.time.Clock()
        self.networking = ClientNetworking(self)
        self.config: ClientConfig = self._get_config()
        self.renderer = ClientRenderer(self)
        self.map: Map | None = None
        self.running = True
        self.player = None  # gets assigned when we "get" our player from the server
        self.player_uuid = None
        self.entities: list[ClientEntity] = []  # other entities, can also be other players
        self.state = client_state.MAIN_MENU

        self.networking.start()

    def get_all_entities(self) -> list[ClientEntity]:
        """Returns a list of all entities, including the player."""
        return [self.player] + self.entities

    @staticmethod
    def get_config_file():
        config_dir = os.getenv("localappdata")
        if not config_dir or not os.path.exists(config_dir):  # we're probably on linux - todo macos support?
            print(Path.home())
            config_dir = os.path.join(Path.home(), ".TombstoneTunnels")
        else:
            config_dir = os.path.join(config_dir, "TombstoneTunnels")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, "config.json")

    @staticmethod
    def _get_config():
        """Load the client config from config.json."""
        config_file = Client.get_config_file()
        try:
            with open(config_file) as f:
                # load as ClientConfig object
                return json.load(f, object_hook=lambda d: ClientConfig(**d))
        except FileNotFoundError:
            print("config.json not found. Creating default config...")
            config = ClientConfig()
            with open(config_file, "w") as f:
                json.dump(config.__dict__, f, indent=4)
            return config

    def save_config(self):
        """Save the current client config to config.json."""
        config_file = Client.get_config_file()
        with open(config_file, "w") as f:
            json.dump(self.config.__dict__, f, indent=4)

    def set_custom_address(self, address: str):
        """Sets the address of the custom server to connect to."""
        split = address.split(":")
        if len(split) == 1:
            # we have no port
            port = self.networking.DEFAULT_SERVER_PORT
        else:
            port = split[1]

        try:
            self.config.custom_server_address = (split[0], int(port))
        except ValueError:
            pass

    def disconnect(self):
        """Reset variables. Note that networking.disconnect() has to be called separately (when necessary)."""
        self.state = client_state.MAIN_MENU
        self.player = None
        self.player_uuid = None
        self.entities.clear()

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            events = [event for event in pygame.event.get()]
            self.tick(events, dt)
            self.renderer.update(self.state, events, dt)  # camera/ui logic etc.
            self.renderer.render(self.state, dt)
        print("Shutting down...")

    def tick(self, events, dt):
        """Handle events and tick all entities (move them etc., but don't render them)."""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.renderer.toggle_fullscreen()
                elif event.key == pygame.K_F3:
                    self.renderer.debugger.enabled = not self.renderer.debugger.enabled
                elif event.key == pygame.K_ESCAPE:
                    if self.state == client_state.MAIN_MENU:
                        self.running = False
                    else:
                        print("Disconnecting from server...")
                        self.networking.disconnect()
                        self.disconnect()

        for entity in (self.get_all_entities()):
            if entity:
                entity.tick(dt, events)

    def update_player(self, player):
        """Set our player and advise the camera to target the player."""
        self.player = player
        self.renderer.camera_target = player


if __name__ == "__main__":
    client = Client()
    client.run()
    client.save_config()
    print("Saved config.")
