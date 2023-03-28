import pygame, os
# describes a type of Tile, for example a dirt tile



# data type to be stored in the tileTypeManager
class TileType:
    def __init__(self, imgPath:str, solid:bool=False):
        try:
            self.image = pygame.image.load(imgPath).convert_alpha()
        except:
            print(f"failed to load tile from path: {imgPath}")
        self.solid = solid

# contains all possible TileTypes and their names
class TileTypeManager:
    def __init__(self):
        self.tileTypes = {}

    def loadImages(self, path:str):
        for filename in os.listdir(path):
            name = filename[:filename.find(".")]
            self.tileTypes[name] = TileType(path+"\\"+filename)


class TileMap:
    def __init__(self, tileSize:int, pathToTileImgs:str, pathToMapFile:str, pos:pygame.Vector2=pygame.Vector2(0,0)):
        self.tileSize = tileSize
        self.tileTypeManager = TileTypeManager()
        self.tileTypeManager.loadImages(pathToTileImgs)
        self.position = pos

        self.tileMap = [] # list of tile names
        self.loadMapFile(pathToMapFile)

    def loadMapFile(self, path:str):
        try:
            with open(path, "r") as fp:
                data = fp.readlines()
        except:
            print(f"Failed to load mapfile at {path}")
        for index, line in enumerate(data):
            data[index] = line.replace(" ", "").replace("\n", "").split(",")

        self.tileMap = data

    def render(self, surface:pygame.Surface, offset:pygame.Vector2): # unoptimised rendering, assuming tilemap is relatively small
        for y, row in enumerate(self.tileMap):
            for x, tilename in enumerate(row):
                if tilename == "":
                    continue
                surface.blit(
                    self.tileTypeManager.tileTypes[tilename].image,
                    (
                        self.position.x+(x*self.tileSize)+offset.x, 
                        self.position.y+(y*self.tileSize)+offset.y
                    )
                )

        

