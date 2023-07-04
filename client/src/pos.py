from pygame import Vector2

TILE_SIZE = 16  # width and height of the quadratic tiles


def abs_from_tile_pos(tile_pos: Vector2) -> Vector2:
    """Converts a tile position to an absolute position; i.e. the position in scaled (!) pixels."""
    return tile_pos * TILE_SIZE
