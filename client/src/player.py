# This file contains the player object with rendering and physics methods
import copy

import pygame

from client.src.camera import Camera
from common.src.entity.ClientInput import ClientInput
from common.src.packets.c2s.ChangeInputPacket import ChangeInputPacket
from common.src.vec.TilePos import TilePos
from common.src.vec.Vec2i import Vec2i
from vec.AbsPos import AbsPos


class Entity:
    def __init__(self, tile_position: TilePos = TilePos(), direction=Vec2i()):
        self.tile_position: TilePos = tile_position
        self.animated_position: AbsPos = AbsPos.from_tile_pos(tile_position)
        self.direction = direction
        self.max_speed: int = 120
        self.sprite = None  # TODO add custom sprite support

    def render(self, camera: Camera):
        pygame.draw.circle(camera.renderTexture, (255, 0, 0), self.animated_position - camera.position, 5)


class Player(Entity):
    def __init__(self, client, uuid, tile_position: TilePos = TilePos()):
        Entity.__init__(self, tile_position)
        self.client = client  # todo global client instance?
        self.uuid = uuid

        self.inputBuffer = []

    def update(self, delta_time, tile_map, pygame_events):
        self.handle_events(pygame_events)

    def handle_events(self, pygame_events):
        dir = copy.copy(self.direction)
        for event in pygame_events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    dir.x -= 1
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    dir.x += 1
                elif event.key in [pygame.K_w, pygame.K_UP]:
                    dir.y += 1
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    dir.y -= 1

            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    dir.x -= 1
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    dir.x += 1
                elif event.key in [pygame.K_w, pygame.K_UP]:
                    dir.y -= 1
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    dir.y += 1

        # todo only vertical/horizontal movement
        dir.x = max(min(dir.x, 1), -1)
        dir.y = max(min(dir.y, 1), -1)

        if dir != self.direction:
            print("Direction changed; sending packet")
            packet = ChangeInputPacket(ClientInput(dir))
            self.client.send_packet(packet)
