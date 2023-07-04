import os

import wfc
from common.src.map.map import Map

# When using pyinstaller, the data folder is in the root location; otherwise it's in server/src/data
DATA_PATH = os.path.join(os.path.dirname(__file__), "data")  # check pyinstaller path
if not os.path.exists(DATA_PATH):
    # not using pyinstaller
    DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")


class MapManager:
    """
    Class to generate and manage maps. Additionally, there is a method for loading maps from files (see _load_maps()),
    but this is currently not used.
    """
    def __init__(self):
        self.maps = []
        # commented out because map generation was implemented; we don't need to load maps from files anymore
        # self.maps: list[Map] = self._load_maps()
        self.maps.append(self.generate_map())  # adds the generated map to self.maps
        pass

    @staticmethod
    def _load_maps() -> list[Map]:
        """
        Loads all maps from the maps folder.
        :return: A list of all maps.
        """
        maps = []
        for filename in os.listdir(os.path.join(DATA_PATH, "maps")):
            # load all .csv files in the server-side maps folder
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

    @staticmethod
    def generate_map(size: int = 20) -> Map:
        """
        Method to generate a map using our wfc (wave function collapse) utilities. As wfc does not make that much sense
        for our project, we will probably use our own (simpler) method in the future.
        :param size: size of basic platform
        :return: the generated Map instance
        """
        # generate basic platform
        gen_map = t = [["floor_clear"] * size for i in range(size)]

        # generate structures with wfc
        gen_map = wfc.fill_walls(gen_map, size)
        wfc.wfc_fill(gen_map, size)

        return Map("generated", gen_map)
