import pygame

from common.src.packets.c2s.ClientMovePacket import ClientMovePacket


class Entity:
    def __init__(self, position: pygame.Vector2 = pygame.Vector2(0, 0)):
        self.position = position

        self.maxSpeed = 1.7


        self.sprite = None

    def render(self, surface: pygame.Surface):
        pygame.draw.circle(surface, (255, 0, 0), self.position, 5)


class Player(Entity):
    def __init__(self, client, uuid, position: pygame.Vector2 = pygame.Vector2(0, 0)):
        Entity.__init__(self, position)
        self.client = client  # todo global client instance?
        self.uuid = uuid

        self.velocity = pygame.Vector2(0, 0)
        self.friction = 0.1
        self.acceleration = 20

        self.movingUp = False
        self.movingDown = False
        self.movingLeft = False
        self.movingRight = False

    def update(self, deltaTime, pygameEvents):
        self.handleEvents(pygameEvents)
        self.updatePosition(deltaTime)

    def handleEvents(self, pygameEvents):
        for event in pygameEvents:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    self.movingLeft = True
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    self.movingRight = True
                elif event.key in [pygame.K_w, pygame.K_UP]:
                    self.movingUp = True
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    self.movingDown = True

            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    self.movingLeft = False
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    self.movingRight = False
                elif event.key in [pygame.K_w, pygame.K_UP]:
                    self.movingUp = False
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    self.movingDown = False

    def updatePosition(self, deltaTime):
        if self.velocity.x < 0:
            self.velocity.x = min(0, self.velocity.x + self.friction)
        elif self.velocity.x > 0:
            self.velocity.x = max(0, self.velocity.x - self.friction)

        if self.velocity.y < 0:
            self.velocity.y = min(0, self.velocity.y + self.friction)
        elif self.velocity.y > 0:
            self.velocity.y = max(0, self.velocity.y - self.friction)

        fixedAccel = (self.acceleration * deltaTime)

        # scaler is used to solve the problem of diagonal movement being faster because of two force additions.
        scaler = 1
        if (self.movingDown ^ self.movingUp) and (self.movingLeft ^ self.movingRight):
            scaler = .71

        if self.movingRight:
            self.velocity.x = max(min(self.velocity.x+fixedAccel, self.maxSpeed * scaler), -self.maxSpeed * scaler)
        elif self.movingLeft:
            self.velocity.x = max(min(self.velocity.x-fixedAccel, self.maxSpeed * scaler), -self.maxSpeed * scaler)

        if self.movingDown:
            self.velocity.y = max(min(self.velocity.y+fixedAccel, self.maxSpeed * scaler), -self.maxSpeed * scaler)
        elif self.movingUp:
            self.velocity.y = max(min(self.velocity.y-fixedAccel, self.maxSpeed * scaler), -self.maxSpeed * scaler)

        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

        if self.velocity.x != 0 or self.velocity.y != 0:
            # Send new position to server
            move_packet = ClientMovePacket(self.position)
            try:
                self.client.send_packet(move_packet)
            except Exception as e:
                print("Error while sending move packet.")
                print(e)
