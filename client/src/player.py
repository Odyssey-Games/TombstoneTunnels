# This file contains the player object with rendering and physics methods

import pygame, math

from common.src.packets.c2s.ClientMovePacket import ClientMovePacket


class Entity:
    def __init__(self, tilePosition: pygame.Vector2 = pygame.Vector2(0, 0)):
        self.tilePosition = tilePosition
        self.maxSpeed = 120
        self.sprite = None
c
    def render(self, camera):
        pygame.draw.circle(camera.renderTexture, (255, 0, 0), self.getWorldPos()-camera.position, 5)

    def getWorldPos(self):
        return pygame.Vector2(self.tilePosition * self.tileMap.tileSize, self.tilePosition * self.tileMap.tileSize)


class Player(Entity):
    def __init__(self, client, uuid, tilemap, tilePosition: pygame.Vector2 = pygame.Vector2(0, 0)):
        Entity.__init__(self, tilePosition)
        self.client = client  # todo global client instance?
        self.uuid = uuid

        self.inputBuffer = []

    def update(self, deltaTime, tileMap, pygameEvents):
        self.handleEvents(pygameEvents)
        self.updatePosition(deltaTime, tileMap)
        self.sendPacket()

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

    def updatePosition(self, deltaTime, tileMap):
        pass

    def moveAndCollide(self, tilemap, deltaTime):
        pass




def sendPacket(self):
    if self.velocity.x != 0 or self.velocity.y != 0:
        # Send new position to server
        move_packet = ClientMovePacket(self.position)
        try:
            self.client.send_packet(move_packet)
        except Exception as exeption:
            print("Error while sending move packet.")
            print(exeption)



