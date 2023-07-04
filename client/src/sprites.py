import math
from time import time

import pygame.image
from pygame import Surface, Vector2

from assets import Assets
from common.src.direction import Dir2


class EntitySprite:
    """
    Helper class for managing the different sprites (textures) for one entity type and thereby creating
    the animation, based on the current state and direction of the entity.
    """

    def _get_sprites(self, my_type: str):
        """
        :return: a list of pygame surfaces (sprites/images) for the specified entity type
        """
        sprites = []
        try:
            for i in range(0, 4):
                image = pygame.image.load(
                    Assets.get("entities", f"{self.name}_{my_type}_anim_f{i}.png")).convert_alpha()
                sprites.append(image)
        except FileNotFoundError:
            pass
        return sprites

    def _get_offset(self):
        """
        Load the offset from the assets folder, if it exists.
        :return: the offset parsed as a Vector2
        """
        try:
            with open(Assets.get("entities", f"{self.name}_offset.txt"), "r") as f:
                split = f.readline().split(" ")
                return Vector2(int(split[0]), int(split[1]))
        except FileNotFoundError:
            return Vector2(0, 0)

    def __init__(self, name: str, frame_duration: float = 0.2):
        self.name = name
        self.frame_duration = frame_duration  # duration of one frame in seconds
        self.last_frame_time = time()  # time of the last frame change
        self.current_frame = 0  # current frame index
        self.idle_sprites = self._get_sprites("idle")  # list of idle sprites
        self.run_sprites = self._get_sprites("run")  # list of running sprites
        self.hit_sprites = self._get_sprites("hit")  # list of hit sprites
        self.offset = self._get_offset()  # offset of the sprite

    def current_sprite(self, running: bool = False, attacking: bool = False) -> (Surface, Vector2):
        if attacking:
            # if the entity is attacking, we use the hit sprites if they exist, otherwise the idle sprites
            if len(self.hit_sprites) > 0:
                sprites = self.hit_sprites
            else:
                sprites = self.idle_sprites
        else:
            # if the entity is not attacking, we use the running sprites if they are running, otherwise the idle sprites
            sprites = self.run_sprites if running else self.idle_sprites
        if (time() - self.last_frame_time) >= self.frame_duration:
            # if the time since the last frame change is greater than the frame duration, we change the frame
            self.last_frame_time = time()
            self.current_frame += 1
            if self.current_frame >= len(sprites):
                self.current_frame = 0

        try:
            # try to return the current frame, extra check so that we don't crash because we have no sprites
            return sprites[self.current_frame], self.offset
        except IndexError:
            return sprites[0], self.offset


class WeaponSprite:
    """
    Helper class for managing weapon sprites and returning the correctly applied rotation.
    Loads the weapon sprite and offset from the assets folder.
    """

    def _get_sprite(self) -> Surface:
        """
        :return: the unrotated pygame image for our weapon sprite
        """
        return pygame.image.load(Assets.get("weapons", f"weapon_{self.name}.png")).convert_alpha()

    def _get_offset(self):
        """
        Load the offset from the assets folder, if it exists.
        :return: the offset parsed as a Vector2
        """
        try:
            with open(Assets.get("weapons", f"{self.name}_offset.txt"), "r") as f:
                split = f.readline().split(" ")
                return Vector2(int(split[0]), int(split[1]))
        except FileNotFoundError:
            return Vector2(0, 0)

    def __init__(self, name: str):
        self.name = name  # name of the weapon; used to load the correct image
        self.sprite = self._get_sprite()
        self.base_offset = self._get_offset()

    def current_surface(self, attacking: bool = False, attack_animation_time=0, last_direction: Dir2 = Dir2.ZERO) -> (Surface, Vector2):
        """
        Get the current pygame surface (image) for the weapon sprite.
        :param attacking: whether the entity (currently player) is attacking
        :param last_direction: the last direction in which the entity faced
        :param attack_animation_time: the time of the last attack, used for animating the sword
        :return: the current image based on the last entity direction
        """
        if attacking:
            base_offset = self.base_offset.copy()

            # cosine function for animating the sword
            animation_offset = math.cos((2*math.pi/0.5)*(time()))

            # animate sprite based on the time since the last action (move sprite forward and back)
            base_offset += last_direction.to_tile_vector() * animation_offset * 2 + last_direction.to_tile_vector() * 2

            if last_direction == Dir2.UP:
                return self.sprite, base_offset
            elif last_direction == Dir2.DOWN:
                return pygame.transform.rotate(self.sprite, 180), base_offset + Vector2(0, 16)
            elif last_direction == Dir2.LEFT:
                return pygame.transform.rotate(self.sprite, 90), base_offset + Vector2(-16, 16)
            elif last_direction == Dir2.RIGHT:
                return pygame.transform.rotate(self.sprite, 270), base_offset + Vector2(0, 16)
            else:
                return self.sprite, base_offset
        else:
            return None, self.base_offset
