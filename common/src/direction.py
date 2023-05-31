from enum import Enum

import pygame
from pygame import Vector2


class Dir2(Enum):
    """Enum for the vertical/horizontal directions in 2D space"""
    ZERO = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def __str__(self):
        return self.name

    def to_tile_vector(self) -> pygame.Vector2:
        return {
            Dir2.UP: Vector2(0, -1),
            Dir2.DOWN: Vector2(0, 1),
            Dir2.LEFT: Vector2(-1, 0),
            Dir2.RIGHT: Vector2(1, 0)
        }.get(self, Vector2(0, 0))
