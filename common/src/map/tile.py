class Tile:
    def __init__(self, name: str):
        self.name = name
        self.is_empty = (name == '')
        self.is_solid = (name[0] == 's') if not self.is_empty else False