# This file contains all the functionality for loading, storing and rendering the tilemap

import os
import pygame


# describes a type of Tile, for example a dirt tile


# data type to be stored in the tileTypeManager
class TileType:
    def __init__(self, imgPath: str, isSolid: bool = False):
        try:
            self.image = pygame.image.load(imgPath).convert_alpha()
        except Exception:
            print(f"failed to load tile from path: {imgPath}")
        self.isSolid = isSolid


# contains all possible TileTypes and their names
class TileTypeManager:
    def __init__(self):
        self.tileTypes = {}

    def loadImages(self, path: str):
        for filename in os.listdir(path):
            name = filename[:filename.find(".")]
            solid = (name[0] == "s")
            self.tileTypes[name] = TileType(os.path.join(path, filename), solid)


class TileMap:
    def __init__(self, tileSize: int, pathToTileImgs: str, pathToMapFile: str,
                 pos: pygame.Vector2 = pygame.Vector2(0, 0)):
        self.tileSize = tileSize
        self.tileTypeManager = TileTypeManager()
        self.tileTypeManager.loadImages(pathToTileImgs)
        self.position = pos

        self.tileMap = []  # list of tile names
        self.loadMapFile(pathToMapFile)

    def loadMapFile(self, path: str):
        try:
            with open(path, "r") as fp:
                data = fp.readlines()
        except:
            print(f"Failed to load mapfile at {path}")
        for index, line in enumerate(data):
            data[index] = line.replace(" ", "").replace("\n", "").split(",")

        self.tileMap = data

    def render(self, camera):  # unoptimised rendering, assuming tilemap is relatively small
        for y, row in enumerate(self.tileMap):
            for x, tilename in enumerate(row):
                if tilename == "":
                    continue
                
                camera.renderTexture.blit(
                    self.tileTypeManager.tileTypes[tilename].image,
                    (
                        self.position.x + (x * self.tileSize) - camera.position.x,
                        self.position.y + (y * self.tileSize) - camera.position.y
                    )
                )
