import os
from typing import Dict

from common.src.map.map import Map
from common.src.map.tile import Tile
from common.src.vec.TilePos import TilePos

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_PATH):  # for pyinstaller; different data folder loc
    DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data")


class MapManager:
    def __init__(self):
        self.maps: list[Map] = self._load_maps()

    @staticmethod
    def _load_maps() -> list[Map]:
        maps = []
        for filename in os.listdir(os.path.join(DATA_PATH, "maps")):
            if filename.endswith(".csv"):
                tiles: list[list[Tile]] = []
                with open(os.path.join(DATA_PATH, "maps", filename)) as f:
                    for line in f:
                        tiles_in_line: list[Tile] = []
                        for tile_name in line.replace(" ", "").replace("\n", "").split(","):
                            tiles_in_line.append(Tile(tile_name))
                        tiles.append(tiles_in_line)
                map_name = filename.removesuffix(".csv")
                maps.append(Map(map_name, tiles))
                print("Loaded map", map_name)
        return maps
