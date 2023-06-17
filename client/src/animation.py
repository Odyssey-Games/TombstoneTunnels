from time import time

from pygame import Surface


class AnimatedSprite:
    def __init__(self, textures: Surface, width: int, frame_count: int, offset: int = 0,
                 frame_duration: float = 0.2):
        self.sprites = []
        self.offset = offset
        height = textures.get_height()
        for i in range(self.offset, self.offset + frame_count):
            self.sprites.append(textures.subsurface(i * width, 0, width, height))

        self.frame_duration = frame_duration
        self.last_frame_time = time()
        self.current_frame = 0

    def current_sprite(self) -> Surface:
        if (time() - self.last_frame_time) >= self.frame_duration:
            self.last_frame_time = time()
            self.current_frame += 1
            if self.current_frame >= len(self.sprites):
                self.current_frame = 0

        return self.sprites[self.current_frame]
