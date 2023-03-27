import pygame, os
# describes a type of Tile, for example a dirt tile



# data type to be stored in the tileTypeManager
class TileType:
    def __init__(self, imgPath, solid:bool=False):
        self.image = pygame.image.load(imgPath).convert_alpha()
        self.solid = solid

# contains all possible TileTypes and their names
class TileTypeManager:
    def __init__(self):
        self.tileTypes = {}

    def loadImages(self, path):
        for filename in os.listdir(path):
            name = filename[:filename.find(".")]
            self.tileTypes[name] = TileType(path+"\\"+filename)

class TileMap:
    def __init__(self, size, pathToTileImgs):
        self.tileTypeManager = TileTypeManager()
        self.tileTypeManager.loadImages(pathToTileImgs)
        self.tileMap = [[] for x in range(size)] # list of tile names

    def loadMapFile(self, path):
        with open(path, "r") as fp:
            data = fp.readlines()

        for line in data:
            data[line] = data[line].replace(" ", "").split(",")
