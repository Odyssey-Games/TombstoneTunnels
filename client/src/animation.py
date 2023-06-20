from time import time

from pygame import Surface, Vector2
import pygame.image

from assets import Assets


class AnimatedSprite:
    def _get_sprites(self, my_type: str):
        sprites = []
        try:
            for i in range(0, 4):
                image = pygame.image.load(Assets.get("entities", f"{self.name}_{my_type}_anim_f{i}.png")).convert_alpha()
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

    def current_sprite(self, running: bool = False) -> (Surface, Vector2):
        sprites = self.run_sprites if running else self.idle_sprites
        if (time() - self.last_frame_time) >= self.frame_duration:
            self.last_frame_time = time()
            self.current_frame += 1
            if self.current_frame >= len(sprites):
                self.current_frame = 0

        return sprites[self.current_frame], self.offset
