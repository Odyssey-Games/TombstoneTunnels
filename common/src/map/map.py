from common.src.map.tile import Tile


class Map:
    """Represents a map of tiles."""

    def __init__(self, name: str, tiles: list[list[Tile]]):
        self.name = name
        self.tiles = tiles

    def __str__(self):
        return f"Map({self.name})"
