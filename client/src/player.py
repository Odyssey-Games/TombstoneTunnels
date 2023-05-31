# This file contains the client-side entity/player classes with methods for rendering
import random

import pygame
from pygame import Vector2

from assets import Assets
from common.src.direction import Dir2
from common.src.packets import *
from pos import abs_from_tile_pos


class ClientEntity:
    ANIMATION_SPEED = 30

    def __init__(self, tile_position: Vector2 = Vector2(), direction=Dir2.ZERO):
        self.tile_position: Vector2 = tile_position
        self.animated_position: Vector2 = abs_from_tile_pos(tile_position)
        self.direction = direction
        self.flip_image = (direction == Dir2.LEFT)
        self.image = pygame.image.load(Assets.get("player", "player.png")).convert_alpha()
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def tick(self, delta_time, events):
        target_position = abs_from_tile_pos(self.tile_position)
        animation_factor = delta_time * self.ANIMATION_SPEED
        if self.animated_position != target_position:
            if 0 < animation_factor < 1:
                self.animated_position = self.animated_position.lerp(target_position, animation_factor)
            else:
                # we don't have enough frames to lerp; just move the player instantly
                self.animated_position = target_position

    def render(self, camera):
        pos = self.animated_position - camera.position
        if self.flip_image:
            flipped_image = pygame.transform.flip(self.image, True, False)
            camera.renderTexture.blit(flipped_image, (pos.x, pos.y - 16))
        else:
            camera.renderTexture.blit(self.image, (pos.x, pos.y - 16))


class ClientPlayer(ClientEntity):
    def __init__(self, client, name, uuid, tile_position: Vector2 = Vector2()):
        ClientEntity.__init__(self, tile_position)
        self.client = client
        self.name = name
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

        if pygame.K_d in self.pressed_keys or pygame.K_RIGHT in self.pressed_keys:
            direction = Dir2.RIGHT
        elif pygame.K_a in self.pressed_keys or pygame.K_LEFT in self.pressed_keys:
            direction = Dir2.LEFT
        elif pygame.K_w in self.pressed_keys or pygame.K_UP in self.pressed_keys:
            direction = Dir2.UP
        elif pygame.K_s in self.pressed_keys or pygame.K_DOWN in self.pressed_keys:
            direction = Dir2.DOWN

        if direction != self.direction:
            packet = ChangeInputPacket(direction.value)
            self.client.send_packet(packet)

            # only flip image when necessary, we don't want the texture to flip back when the player stops moving
            if direction == Dir2.LEFT:
                self.flip_image = True
            elif direction == Dir2.RIGHT:
                self.flip_image = False

            self.direction = direction

    def render(self, camera):
        super().render(camera)

        # render nametag
        pos = self.animated_position - camera.position
        font = pygame.font.SysFont("Arial", 10)
        text = font.render(self.name, True, (255, 255, 255))
        camera.renderTexture.blit(text, (pos.x - text.get_width() / 2 + 8, pos.y - 20))
