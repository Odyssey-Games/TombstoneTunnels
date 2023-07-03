from pygame import Vector2


class Tile:
    def __init__(self, name: str):
        self.name = name
        self.is_empty = (name == '')
        self.is_solid = (name[0] == 's') if not self.is_empty else False

    @staticmethod
    def from_name(name: str):
        return Tile(name)

    @staticmethod
    def from_coords(server, vec: Vector2):
        try:
            return Tile.from_name(server.current_map.tiles[int(vec.y)][int(vec.x)])
        except IndexError:
            return Tile.from_name('s')
