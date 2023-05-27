from common.src.vec.TilePos import TilePos
from common.src.vec.Vec2i import Vec2i

TILE_SIZE = 16


class AbsPos(Vec2i):
    """
    Wrapper class to avoid confusion between absolute positions and other 2d vectors.

    As the server always sends tile positions to clients, absolute positions are only needed on the client side.
    """

    def __init__(self, x: int, y: int):
        super().__init__(x, y)

    def to_tile_pos(self):
        """Converts this absolute position to a tile position."""
        return TilePos(self.x // TILE_SIZE, self.y // TILE_SIZE)

    @staticmethod
    def from_tile_pos(tile_pos: TilePos):
        """Converts the given tile position to an absolute position (in the middle of one tile)."""
        return AbsPos(tile_pos.x * TILE_SIZE, tile_pos.y * TILE_SIZE)

    def __str__(self) -> str:
        """
        Returns a string representation of this absolute position vector.

        :return: a string representation of the vector
        """
        return f"AbsPos({self.x}, {self.y})"

    def lerp(self, tile_position, param):
        """
        Linearly interpolates between this absolute position and the given tile position.

        :param tile_position: the tile position to interpolate to
        :param param: the interpolation parameter
        :return: the interpolated absolute position
        """
        return AbsPos(self.x + (tile_position.x * TILE_SIZE - self.x) * param,
                      self.y + (tile_position.y * TILE_SIZE - self.y) * param)
