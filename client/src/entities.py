# This file contains the client-side entity/player classes with methods for rendering
import random
from time import time

import pygame
from pygame import Vector2

from sprites import WeaponSprite, EntitySprite
from common.src.direction import Dir2
from common.src.entities import EntityType
from common.src.packets import *
from pos import abs_from_tile_pos


class ClientEntity:
    ANIMATION_SPEED = 10
    DAMAGE_ANIMATION_DURATION = 0.2  # seconds

    def __init__(self, uuid: str, entity_type: EntityType, tile_position: Vector2 = Vector2(), health: int = 50,
                 hostile: bool = False):
        self.uuid = uuid
        self.entity_type = entity_type
        self.health = health
        self.tile_position: Vector2 = tile_position
        self.animated_position: Vector2 = abs_from_tile_pos(tile_position)
        self.direction = Dir2.ZERO
        self.last_direction = Dir2.ZERO
        self.attacking = False
        self.flip_image = (self.direction == Dir2.LEFT)
        self.sprite = EntitySprite(self.entity_type.value)
        self.weapon_sprite: WeaponSprite | None = WeaponSprite("knight_sword") if self.entity_type == EntityType.KNIGHT else None
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.hostile = hostile
        self.max_health = health
        self.damage_animation_time = 0

    def tick(self, delta_time, events):
        target_position = abs_from_tile_pos(self.tile_position)
        animation_factor = delta_time * self.ANIMATION_SPEED
        if self.animated_position != target_position:
            if 0 < animation_factor < 1:
                self.animated_position = self.animated_position.lerp(target_position, animation_factor)
            else:
                # we don't have enough frames to lerp; just move the player instantly
                self.animated_position = target_position

    def render(self, camera, dt):
        current_sprite, offset = self.sprite.current_sprite(self.direction != Dir2.ZERO, self.attacking)
        sprite = current_sprite
        if time() - self.damage_animation_time <= self.DAMAGE_ANIMATION_DURATION:
            sprite = pygame.transform.laplacian(sprite)
        pos = self.animated_position - camera.position
        if self.flip_image:
            flipped_image = pygame.transform.flip(sprite, True, False)
            camera.renderTexture.blit(flipped_image, (pos.x, pos.y - 16) + offset)
        else:
            camera.renderTexture.blit(sprite, (pos.x, pos.y - 16) + offset)
        if self.weapon_sprite:
            try:
                weapon, offset = self.weapon_sprite.current_surface(self.attacking, self.last_direction)
                camera.renderTexture.blit(weapon, (pos.x, pos.y - 16) + offset)
            except TypeError:
                pass


class ClientPlayer(ClientEntity):
    def __init__(self, client, name, uuid, tile_position: Vector2 = Vector2(), health: int = 50):
        ClientEntity.__init__(self, uuid, EntityType.KNIGHT, tile_position, health)
        self.client = client
        self.name = name
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
        attacking = pygame.K_SPACE in self.pressed_keys

        if attacking != self.attacking or direction != self.direction:
            packet = ChangeInputPacket(direction.value, attacking)
            self.client.send_packet(packet)

            # only flip image when necessary, we don't want the texture to flip back when the player stops moving
            if direction == Dir2.LEFT:
                self.flip_image = True
            elif direction == Dir2.RIGHT:
                self.flip_image = False

            self.direction = direction
            if self.direction != Dir2.ZERO:
                self.last_direction = self.direction
            self.attacking = attacking

    def render(self, camera, dt):
        super().render(camera, dt)

        # render nametag
        pos = self.animated_position - camera.position
        font = pygame.font.SysFont("Arial", 10)
        text = font.render(self.name, True, (255, 255, 255))
        camera.renderTexture.blit(text, (pos.x - text.get_width() / 2 + 8, pos.y - 20))
