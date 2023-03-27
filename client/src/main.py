import pygame
from pygame.locals import *

from tilemap import *

PATHTOTILEIMAGES = "TombstoneTunnels\\client\\assets\\tilemap\\tiles"

pygame.init()

pygame.display.set_mode((500,600))

running = True

tileMap = TileMap(16, PATHTOTILEIMAGES)
print(tileMap.tileTypeManager.tileTypes)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False