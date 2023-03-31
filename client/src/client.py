from camera import *
from client_networking import ClientNetworking
from client_renderer import ClientRenderer


class Client:
    MAIN_MENU = 0
    CONNECTING = 1
    IN_GAME = 2

    def __init__(self):
        pygame.init()  # we need to call init() before we can use pygame fonts for rendering
        self.clock = pygame.time.Clock()
        self.networking = ClientNetworking(self, "Client " + str(random.randint(1, 10000)))
        self.renderer = ClientRenderer(self)
        self.running = True
        self.player = None  # gets assigned when we "get" our player from the server
        self.player_uuid = None
        self.entities = []  # other entities, can also be other players
        self.state = self.MAIN_MENU

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            events = [event for event in pygame.event.get()]
            if self.state == self.IN_GAME:
                if not self.networking.tick(events, dt):
                    # disconnected from server; go to main menu
                    print("Disconnected from server.")
                    self.state = self.MAIN_MENU
                    self.player = None
                    self.player_uuid = None
            self.tick(events, dt)
            self.renderer.tick(events, dt)

    def tick(self, events, dt):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state == self.MAIN_MENU:
                    print("Exiting...")
                    self.running = False
                else:
                    print("Disconnecting from server...")
                    self.networking.disconnect()
                    self.state = self.MAIN_MENU
                    self.player = None
                    self.player_uuid = None

        if self.player:
            self.player.update(dt, events)

    def update_player(self, player):
        """Set our player and advise the camera to target the player."""
        self.player = player
        self.renderer.camera.target = player


if __name__ == "__main__":
    client = Client()
    client.run()
