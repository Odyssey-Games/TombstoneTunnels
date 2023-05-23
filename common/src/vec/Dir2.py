from enum import Enum

from common.src.vec.Vec2i import Vec2i


class Dir2(Enum):
    """Enum for the vertical/horizontal directions in 2D space"""
    ZERO = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def __str__(self):
        return self.name

    def to_vector(self) -> Vec2i:
        return {
            Dir2.UP: Vec2i(0, -1),
            Dir2.DOWN: Vec2i(0, 1),
            Dir2.LEFT: Vec2i(-1, 0),
            Dir2.RIGHT: Vec2i(1, 0)
        }.get(self, Vec2i(0, 0))
