# Main entry point of the program

import client_state
from camera import *
from client_networking import ClientNetworking
from client_renderer import ClientRenderer
from common.src.map.map import Map
from player import ClientEntity


class Client:
    def __init__(self):
        pygame.init()  # we need to call init() before we can use pygame fonts for rendering
        self.clock = pygame.time.Clock()
        self.server_list = ["localhost", "odysseygames.de"]
        self.current_server_ip = self.server_list[0]
        self.networking = ClientNetworking(self, "Client " + str(random.randint(1, 10000)))
        self.renderer = ClientRenderer(self)
        self.map: Map = None
        self.running = True
        self.player = None  # gets assigned when we "get" our player from the server
        self.player_uuid = None
        self.entities: list[ClientEntity] = []  # other entities, can also be other players
        self.state = client_state.MAIN_MENU

    def _disconnect(self):
        """Reset variables. Note that networking.disconnect() has to be called separately (when necessary)."""
        self.state = client_state.MAIN_MENU
        self.player = None
        self.player_uuid = None
        self.entities.clear()

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            events = [event for event in pygame.event.get()]
            if self.state == client_state.IN_GAME or self.state == client_state.CONNECTING:
                if not self.networking.tick(events, dt):
                    # disconnected from server; go to main menu
                    print("Disconnected from server.")
                    self._disconnect()
            self.tick(events, dt)
            self.renderer.tick(self.state, events, dt)

    def tick(self, events, dt):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == client_state.MAIN_MENU:
                    print("Exiting...")
                    self.running = False
                else:
                    print("Disconnecting from server...")
                    self.networking.disconnect()
                    self._disconnect()

        if self.player:
            self.player.update(dt, self.renderer.tilemap, events)
            # self.renderer.debugger.debug(f"velocity: {self.player.velocity}")
            # self.renderer.debugger.debug(f"position: {self.player.position}")

    def update_player(self, player):
        """Set our player and advise the camera to target the player."""
        self.player = player
        self.renderer.camera.target = player


if __name__ == "__main__":
    client = Client()
    client.run()
