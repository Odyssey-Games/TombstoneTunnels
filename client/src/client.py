from camera import *
from client_networking import ClientNetworking
from client_renderer import ClientRenderer


class Client:
    def __init__(self):
        pygame.init()  # we need to call init() before we can use pygame fonts for rendering
        self.clock = pygame.time.Clock()
        self.networking = ClientNetworking(self, "Client " + str(random.randint(1, 10000)))
        self.renderer = ClientRenderer(self)
        self.running = True
        self.player = None  # gets assigned when we "get" our player from the server
        self.player_uuid = None
        self.entities = []  # other entities, can also be other players

    def run(self):
        self.networking.try_login()
        while self.running:
            dt = self.clock.tick() / 1000
            events = [event for event in pygame.event.get()]
            if not self.networking.tick(events, dt):
                # todo just disconnect from server (go to main menu?)
                raise Exception("Error while ticking networking.")
            self.tick(events, dt)
            self.renderer.tick(events, dt)

    def tick(self, events, dt):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

        if self.player:
            self.player.update(dt, events)

    def update_player(self, player):
        """Set our player and advise the camera to target the player."""
        self.player = player
        self.renderer.camera.target = player


if __name__ == "__main__":
    client = Client()
    client.run()
