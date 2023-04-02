import random, os, pygame

from tilemap import TileMap

# Rooms contain a tilemap and information about all portals
class Room:
    def __init__(self, tilemap:TileMap, portals:str):
        self.tileMap = tilemap
        
        # portals
        self.up = "w" in portals
        self.right = "d" in portals
        self.down = "s" in portals
        self.left = "a" in portals


class MapGenerator:
    def __init__(self, pathToMaps, pathToImages, tileSize, seed):
        self.PATH_TO_MAPS = pathToMaps
        self.PATH_TO_TILE_IMAGES = pathToImages
        self.TILESIZE = tileSize

        self.allRooms = []
        self.loadAllRooms()

        self.roomMap = [] # contains the final room layout
        self.generateMaps(seed, 10)

    def loadAllRooms(self):
        for filename in os.listdir(self.PATH_TO_MAPS):
            portals = filename[:filename.find("_")]
            self.allRooms.append(
                Room(
                    tilemap=TileMap(
                        tileSize=self.TILESIZE, 
                        pathToTileImgs=self.PATH_TO_TILE_IMAGES, 
                        pathToMapFile=os.path.join(self.PATH_TO_MAPS, filename), 
                        pos=pygame.Vector2(0,0)
                    ),
                    portals=portals
                )
            )
        print(f"rooms:\n{self.allRooms}")

    def generateMaps(self, seed, mapSize):
        random.seed(seed)

        # initial assignment
        for y in range(self.mapSize):
            for x in range(self.mapSize):
                self.allRooms[y][x] = [room for room in self.allRooms]
        
        allCollapsed = False
        while not allCollapsed:
            for y in range(self.mapSize):
                for x in range(self.mapSize):
                    self.allRooms[y][x] = [room for room in self.allRooms]
            
