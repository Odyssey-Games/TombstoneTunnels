# This file contains the player object with rendering and physics methods

import pygame

from common.src.entity.ClientInput import ClientInput
from common.src.packets.c2s.ChangeInputPacket import ChangeInputPacket
from common.src.vec.Dir2 import Dir2
from common.src.vec.TilePos import TilePos
from vec.AbsPos import AbsPos


class Entity:
    def __init__(self, tile_position: TilePos = TilePos(), direction=Dir2.ZERO):
        self.tile_position: TilePos = tile_position
        self.animated_position: AbsPos = AbsPos.from_tile_pos(tile_position)
        self.direction = direction
        self.max_speed: int = 120
        self.sprite = None  # TODO add custom sprite support

    def render(self, camera):
        center = self.animated_position - camera.position
        pygame.draw.circle(camera.renderTexture, (255, 0, 0), (center.x, center.y), 5)


class Player(Entity):
    def __init__(self, client, uuid, tile_position: TilePos = TilePos()):
        Entity.__init__(self, tile_position)
        self.client = client  # todo global client instance?
        self.uuid = uuid
        self.pressed_keys = set()

    def update(self, delta_time, tile_map, pygame_events):
        self.handle_events(pygame_events)

    def handle_events(self, pygame_events):
        direction = Dir2.ZERO
        for event in pygame_events:
            if event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)
            elif event.type == pygame.KEYUP:
                self.pressed_keys.remove(event.key)

        if pygame.K_d in self.pressed_keys:
            direction = Dir2.RIGHT
        elif pygame.K_a in self.pressed_keys:
            direction = Dir2.LEFT
        elif pygame.K_w in self.pressed_keys:
            direction = Dir2.UP
        elif pygame.K_s in self.pressed_keys:
            direction = Dir2.DOWN

        if direction != self.direction:
            print("Direction changed; sending packet")
            packet = ChangeInputPacket(ClientInput(direction))
            self.client.send_packet(packet)

        self.direction = direction
