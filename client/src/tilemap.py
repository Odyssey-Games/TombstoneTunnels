"""This file contains all the functionality for loading, storing and rendering the tilemap"""

import os

import pygame


class TileType:
    """
    Describe a type of tile, for example a dirt tile.

    This is a data type to be stored in the tile type manager.
    """

    def __init__(self, img_path: str, is_solid: bool = False):
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except Exception as e:
            print(f"failed to load tile from path '{img_path}': {e}")
        self.is_solid = is_solid


# contains all possible TileTypes and their names
class TileTypeManager:
    def __init__(self):
        self.tileTypes = {}

    def load_images(self, path: str):
        for filename in os.listdir(path):
            name = filename[:filename.find(".")]
            solid = (name[0] == "s")
            self.tileTypes[name] = TileType(os.path.join(path, filename), solid)


class TileMap:
    def __init__(self, tile_size: int, path_to_tile_imgs: str, path_to_map_file: str,
                 pos: pygame.Vector2 = pygame.Vector2(0, 0)):
        self.tile_size = tile_size
        self.type_manager = TileTypeManager()
        self.type_manager.load_images(path_to_tile_imgs)
        self.position = pos

        self.map: list[list[str]] = []  # two-dimensional list of tile names -> tileMap[y][x]
        self.load_map_file(path_to_map_file)

    def load_map_file(self, path: str):
        """
        Loads a map from a tile map file. The file should be a csv file with the tile names separated by commas.
        """
        try:
            with open(path, "r") as fp:
                lines = fp.readlines()
                data: list[list[str]] = [[] for _ in range(len(lines))]

                for index, line in enumerate(lines):
                    data[index] = line.replace(" ", "").replace("\n", "").split(",")

                self.map = data
        except Exception as e:
            print(f"Failed to load map file at '{path}': {e}")
            raise e

    def render(self, camera):  # unoptimised rendering, assuming tilemap is relatively small
        for y, row in enumerate(self.map):
            for x, tile_name in enumerate(row):
                if tile_name == "":  # ignore empty tiles
                    continue

                camera.renderTexture.blit(
                    self.type_manager.tileTypes[tile_name].image,
                    (
                        self.position.x + (x * self.tile_size) - camera.position.x,
                        self.position.y + (y * self.tile_size) - camera.position.y
                    )
                )
