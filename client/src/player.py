import pygame, math

from common.src.packets.c2s.PlayerMovePacket import PlayerMovePacket


class Entity:
    def __init__(self, position: pygame.Vector2 = pygame.Vector2(0, 0)):
        self.position = position

        self.maxSpeed = 120


        self.sprite = None

    def render(self, camera):
        pygame.draw.circle(camera.renderTexture, (255, 0, 0), self.position-camera.position, 5)


class Player(Entity):
    def __init__(self, client, position: pygame.Vector2 = pygame.Vector2(0, 0)):
        Entity.__init__(self, position)
        self.client = client  # todo global client instance?
        
        self.velocity = pygame.Vector2(0, 0)
        self.friction = 0.02
        self.acceleration = 50

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
        fixedFrict = pow(self.friction, deltaTime)
        self.velocity.y *= fixedFrict
        self.velocity.x *= fixedFrict

        if self.velocity.x > -0.001 and self.velocity.x < 0.001:
            self.velocity.x = 0
        if self.velocity.y > -0.001 and self.velocity.y < 0.001:
            self.velocity.y = 0

        # scaler is used to solve the problem of dioganal movement being faster because of two force additions. 
        scaler = 1
        if (self.movingDown ^ self.movingUp) and (self.movingLeft ^ self.movingRight):
            scaler = .71

        fixedAccel = self.acceleration * deltaTime * 10
        fixedMaxSpeed = self.maxSpeed

        if self.movingRight:
            self.velocity.x = max(min(self.velocity.x+fixedAccel, fixedMaxSpeed * scaler), -fixedMaxSpeed * scaler) 
        elif self.movingLeft:  
            self.velocity.x = max(min(self.velocity.x-fixedAccel, fixedMaxSpeed * scaler), -fixedMaxSpeed * scaler)
  
        if self.movingDown:  
            self.velocity.y = max(min(self.velocity.y+fixedAccel, fixedMaxSpeed * scaler), -fixedMaxSpeed * scaler) 
        elif self.movingUp:  
            self.velocity.y = max(min(self.velocity.y-fixedAccel, fixedMaxSpeed * scaler), -fixedMaxSpeed * scaler)

        self.position.x += self.velocity.x * deltaTime
        self.position.y += self.velocity.y * deltaTime

        if self.velocity.x != 0 or self.velocity.y != 0:
            # Send new position to server
            move_packet = PlayerMovePacket(self.position)
            self.client.send_packet(move_packet)
