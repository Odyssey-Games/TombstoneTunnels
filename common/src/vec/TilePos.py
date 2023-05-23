from common.src.vec.Vec2i import Vec2i


class TilePos(Vec2i):
    """Wrapper class to avoid confusion between tile positions and other 2d vectors."""

    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y)

    def __str__(self) -> str:
        """
        Returns a string representation of this tile position vector.

        :return: a string representation of the vector
        """
        return f"TilePos({self.x}, {self.y})"
