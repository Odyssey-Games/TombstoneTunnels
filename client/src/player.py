# This file contains the player object with rendering and physics methods

import pygame, math

from common.src.packets.c2s.ClientMovePacket import ClientMovePacket


class Entity:
    def __init__(self, position: pygame.Vector2 = pygame.Vector2(0, 0)):
        self.position = position
        self.hitbox = pygame.Rect(100,100,10,10)

        self.maxSpeed = 120


        self.sprite = None

    def render(self, camera):
        pygame.draw.circle(camera.renderTexture, (255, 0, 0), self.position-camera.position, 5)


class Player(Entity):
    def __init__(self, client, uuid, position: pygame.Vector2 = pygame.Vector2(0, 0)):
        Entity.__init__(self, position)
        self.client = client  # todo global client instance?
        self.uuid = uuid

        self.velocity = pygame.Vector2(0, 0)
        self.friction = 0.025
        self.acceleration = 60

        self.movingUp = False
        self.movingDown = False
        self.movingLeft = False
        self.movingRight = False

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
        fixedFrict = pow(self.friction, deltaTime)
        self.velocity.y *= fixedFrict
        self.velocity.x *= fixedFrict

        if self.velocity.x > -0.001 and self.velocity.x < 0.001:
            self.velocity.x = 0
        if self.velocity.y > -0.001 and self.velocity.y < 0.001:
            self.velocity.y = 0

        # scaler is used to solve the problem of diagonal movement being faster because of two force additions.
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

        self.moveAndCollide(tileMap, deltaTime)


    def sendPacket(self):
        if self.velocity.x != 0 or self.velocity.y != 0:
            # Send new position to server
            move_packet = ClientMovePacket(self.position)
            try:
                self.client.send_packet(move_packet)
            except Exception as exeption:
                print("Error while sending move packet.")
                print(exeption)
    

    def moveAndCollide(self, tilemap, deltaTime):
        tilesToCheck = []
        for y, row in enumerate(tilemap.tileMap):
            for x, tile in enumerate(row):
                if tilemap.tileTypeManager.tileTypes[tile].isSolid:
                    tilesToCheck.append(
                        pygame.Rect(
                            tilemap.position.x + (x * tilemap.tileSize),
                            tilemap.position.y + (y * tilemap.tileSize),
                            tilemap.tileSize,
                            tilemap.tileSize
                        )
                    )
        
    #### check for x movement-collisions:
       
        self.position.x += self.velocity.x * deltaTime
        
        # -5 to convert circle center pos to rect top-left edge pos with current radius of 5 
        self.hitbox.x = self.position.x-5
        self.hitbox.y = self.position.y-5

        hitTiles = []
        for tile in tilesToCheck:
            if self.hitbox.colliderect(tile):
                hitTiles.append(tile)

        for tile in hitTiles:     
            if self.velocity.x > 0:
                self.position.x = int(tile.left - 6)
                self.velocity.x = 0

            elif self.velocity.x < 0:
                self.position.x = int(tile.right + 5)
                self.velocity.x = 0
        
    #### check for y movement-collisions:    
        self.position.y += self.velocity.y * deltaTime

        # -5 to convert circle center pos to rect top-left edge pos with current radius of 5
        self.hitbox.x = self.position.x-5
        self.hitbox.y = self.position.y-5

        hitTiles = []
        for tile in tilesToCheck:
            if self.hitbox.colliderect(tile):
                hitTiles.append(tile)

        for tile in hitTiles:     
            if self.velocity.y > 0:
                self.position.y = int(tile.top - 6)
                self.velocity.y = 0

            elif self.velocity.y < 0:
                self.position.y = int(tile.bottom + 5)
                self.velocity.y = 0
        
    #### Apply movement of hitbox to position


