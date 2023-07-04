from time import time

import pygame.image
from pygame import Surface, Vector2

from assets import Assets
from common.src.direction import Dir2


class EntitySprite:
    def _get_sprites(self, my_type: str):
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
        try:
            with open(Assets.get("entities", f"{self.name}_offset.txt"), "r") as f:
                split = f.readline().split(" ")
                return Vector2(int(split[0]), int(split[1]))
        except FileNotFoundError:
            return Vector2(0, 0)

    def __init__(self, name: str, frame_duration: float = 0.2):
        self.name = name
        self.frame_duration = frame_duration
        self.last_frame_time = time()
        self.current_frame = 0
        self.idle_sprites = self._get_sprites("idle")
        self.run_sprites = self._get_sprites("run")
        self.hit_sprites = self._get_sprites("hit")
        self.offset = self._get_offset()

    def current_sprite(self, running: bool = False, attacking: bool = False) -> (Surface, Vector2):
        if attacking:
            if len(self.hit_sprites) > 0:
                sprites = self.hit_sprites
            else:
                sprites = self.idle_sprites
        else:
            sprites = self.run_sprites if running else self.idle_sprites
        if (time() - self.last_frame_time) >= self.frame_duration:
            self.last_frame_time = time()
            self.current_frame += 1
            if self.current_frame >= len(sprites):
                self.current_frame = 0

        try:
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

    def current_surface(self, attacking: bool = False, last_direction: Dir2 = Dir2.ZERO) -> (Surface, Vector2):
        """
        Get the current pygame surface (image) for the weapon sprite.
        :param attacking: whether the entity (currently player) is attacking
        :param last_direction: the last direction in which the entity faced
        :return: the current image based on the last entity direction
        """
        if attacking:
            if last_direction == Dir2.UP:
                return self.sprite, self.base_offset
            elif last_direction == Dir2.DOWN:
                return pygame.transform.rotate(self.sprite, 180), self.base_offset + Vector2(0, 16)
            elif last_direction == Dir2.LEFT:
                return pygame.transform.rotate(self.sprite, 90), self.base_offset + Vector2(-16, 16)
            elif last_direction == Dir2.RIGHT:
                return pygame.transform.rotate(self.sprite, 270), self.base_offset + Vector2(0, 16)
            else:
                return self.sprite, self.base_offset
        else:
            return None, self.base_offset
