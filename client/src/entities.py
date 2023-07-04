# This file contains the client-side entity/player classes with methods for rendering
import math
import random
from time import time

import pygame
from pygame import Vector2

from common.src.direction import Dir2
from common.src.entities import EntityType
from common.src.packets import *
from pos import abs_from_tile_pos
from sprites import WeaponSprite, EntitySprite


class ClientEntity:
    """
    Represents a client-sided entity in the game world. Can be a player or hostile creature.
    There are different classes for entities on the server, as they have different jobs. For example,
    on the client we only render entities and handle animations, while on the server we handle movement and
    other logic (see server/src/entities.py).
    """
    ANIMATION_SPEED = 10  # how fast the animation is played
    DAMAGE_ANIMATION_DURATION = 0.2  # seconds

    def __init__(self, uuid: str, entity_type: EntityType, tile_position: Vector2 = Vector2(), health: int = 50,
                 hostile: bool = False):
        self.uuid = uuid  # unique identifier of entity
        self.entity_type = entity_type  # type of entity -> used for sprites, animations etc.
        self.health = health  # health points of entity (10 = 1 heart)
        self.tile_position: Vector2 = tile_position  # tile position of entity
        self.animated_position: Vector2 = abs_from_tile_pos(tile_position)  # animated (absolute) position of entity
        self.direction = Dir2.ZERO  # direction of entity input (facing direction)
        self.last_direction = Dir2.ZERO  # last direction of entity input, only ZERO at start
        self.attacking = False  # whether the entity is attacking
        # should the sprite be flipped? (for left/right facing)
        self.flip_image = (self.direction == Dir2.LEFT)
        self.sprite = EntitySprite(self.entity_type.value)
        # if the entity is a knight (player), it has a weapon sprite
        self.weapon_sprite: WeaponSprite | None = WeaponSprite("knight_sword") if self.entity_type == EntityType.KNIGHT else None
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.hostile = hostile  # whether the entity is hostile (e.g. a skeleton)
        self.max_health = health  # the maximum health of the entity; currently used for the health bar
        self.damage_animation_time = 0  # the time the damage animation was started
        self.attack_animation_time = 0  # the time the attack animation was started
        self.spawn_time = time()  # the time the entity was spawned (used for fade-in animation)
        print("RESET SPAWN TIME")

    def tick(self, delta_time, events):
        """
        The tick() function is called each frame. On the client, the only thing we do is move the specific
        entity smoothly in direction of the new position using the lerp() function.
        """
        target_position = abs_from_tile_pos(self.tile_position)
        animation_factor = delta_time * self.ANIMATION_SPEED
        if self.animated_position != target_position:
            if 0 < animation_factor < 1:
                self.animated_position = self.animated_position.lerp(target_position, animation_factor)
            else:
                # we don't have enough frames to lerp; just move the player instantly
                self.animated_position = target_position

    def render(self, camera, dt):
        """
        Render the entity to the screen. This function is called each frame. It renders the entity's sprite
        and weapon sprite (if applicable). It also shows the damage animation. The damage animation is a
        simple laplacian filter applied to the sprite for a short duration.
        """
        current_sprite, offset = self.sprite.current_sprite(self.direction != Dir2.ZERO, self.attacking)
        sprite = current_sprite.copy()  # we don't want to modify the original sprite for fade-in animations
        if time() - self.spawn_time <= 1:
            # fade-in animation
            sprite.set_alpha(int(255 * (time() - self.spawn_time)))
        if time() - self.damage_animation_time <= self.DAMAGE_ANIMATION_DURATION:
            sprite = pygame.transform.laplacian(sprite)
        pos = self.animated_position - camera.position
        if self.flip_image:  # entity is facing left
            flipped_image = pygame.transform.flip(sprite, True, False)
            camera.renderTexture.blit(flipped_image, (pos.x, pos.y - 16) + offset)
        else:
            # entity is facing right
            camera.renderTexture.blit(sprite, (pos.x, pos.y - 16) + offset)
        if self.weapon_sprite:
            # entity has a weapon that should be rendered
            try:
                weapon, offset = self.weapon_sprite.current_surface(self.attacking, self.attack_animation_time, self.last_direction)
                camera.renderTexture.blit(weapon, (pos.x, pos.y - 16) + offset)
            except TypeError as e:
                # weapon sprite doesn't want to render any surface
                pass


class ClientPlayer(ClientEntity):
    """
    The player is a special type of entity that has an additional name. It also handles client-sided input for
    movement and attacking and sends the corresponding packets to the server. The name is rendered above the
    player's head after the sprite is rendered in the above class (ClientEntity).
    """
    def __init__(self, client, name, uuid, tile_position: Vector2 = Vector2(), health: int = 50):
        ClientEntity.__init__(self, uuid, EntityType.KNIGHT, tile_position, health)
        self.client = client
        self.name = name
        self.pressed_keys = set()

    def update(self, delta_time, tile_map, pygame_events):
        """
        The update() function is called each frame. Here, we handle input (movement etc.) and send packets
        to the server. Rendering is handled in the render() function.
        """
        self.handle_events(pygame_events)

    def handle_events(self, pygame_events):
        """
        Handle pygame events and send packets to the server if necessary.
        Events handled include movement and attacking.
        """
        direction = Dir2.ZERO
        for event in pygame_events:
            if event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)
            elif event.type == pygame.KEYUP:
                self.pressed_keys.remove(event.key)

        # does the player want to move?
        if pygame.K_d in self.pressed_keys or pygame.K_RIGHT in self.pressed_keys:
            direction = Dir2.RIGHT
        elif pygame.K_a in self.pressed_keys or pygame.K_LEFT in self.pressed_keys:
            direction = Dir2.LEFT
        elif pygame.K_w in self.pressed_keys or pygame.K_UP in self.pressed_keys:
            direction = Dir2.UP
        elif pygame.K_s in self.pressed_keys or pygame.K_DOWN in self.pressed_keys:
            direction = Dir2.DOWN
        # does the player want to attack?
        attacking = pygame.K_SPACE in self.pressed_keys

        if attacking != self.attacking or direction != self.direction:
            # send packet to server; this is only necessary if the player's state has changed
            # (e.g. the player started moving, changed direction or started attacking)
            packet = ChangeInputPacket(direction.value, attacking)
            self.client.send_packet(packet)

            # only flip image when necessary, we don't want the texture to flip back when the player stops moving
            if direction == Dir2.LEFT:
                self.flip_image = True
            elif direction == Dir2.RIGHT:
                self.flip_image = False

            self.direction = direction
            if self.direction != Dir2.ZERO:
                # set last direction; this is used for knowing which direction to attack in
                # (e.g. if the player is moving left and attacks, the attack animation should be left)
                self.last_direction = self.direction
            self.attacking = attacking

    def render(self, camera, dt):
        super().render(camera, dt)  # this renders the player's sprite

        # render nametag; this is done after rendering the player so that the nametag is rendered on top of the player
        pos = self.animated_position - camera.position
        font = pygame.font.SysFont("Arial", 10)
        text = font.render(self.name, True, (255, 255, 255))
        camera.renderTexture.blit(text, (pos.x - text.get_width() / 2 + 8, pos.y - 20))
