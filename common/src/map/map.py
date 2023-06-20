class Map:
    """Represents a map of tiles."""

    def __init__(self, name: str, tiles: list[list[str]]):
        """
        :param name: The name of the map.
        :param tiles: A 2D list of tiles. IMPORTANT: The first index is y, the second index is the x coordinate.
        """
        self.name = name
        self.tiles: list[list[str]] = tiles

    def __str__(self):
        return f"Map({self.name})"
