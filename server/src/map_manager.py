import os

from common.src.map.map import Map
import wfc

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")  # for pyinstaller; different data folder loc
if not os.path.exists(DATA_PATH):
    DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")


class MapManager:
    def __init__(self):
        self.maps = []
        #self.maps: list[Map] = self._load_maps()
        self.generate_map()
        pass
 
    @staticmethod
    def _load_maps() -> list[Map]:
        maps = []
        for filename in os.listdir(os.path.join(DATA_PATH, "maps")):
            if filename.endswith(".csv"):
                tiles: list[list[str]] = []
                with open(os.path.join(DATA_PATH, "maps", filename)) as f:
                    for line in f:
                        tiles_in_line: list[str] = []
                        for tile_name in line.replace(" ", "").replace("\n", "").split(","):
                            tiles_in_line.append(tile_name)
                        tiles.append(tiles_in_line)
                map_name = filename.removesuffix(".csv")
                maps.append(Map(map_name, tiles))
                print("Loaded map", map_name)
        return maps

    def generate_map(self, size:int = 20):
        # generate the client side of the map
        genMap = t = [ ["floor_clear"]*size for i in range(size)]
        
        genMap = wfc.fill_walls(genMap, size)

        wfc.wfc_fill(genMap, size)
        
        
        # begin filling the map using wfc

        self.maps.append(Map("generated",genMap))