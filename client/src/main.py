import pygame
from pygame.locals import *

from tilemap import *

PATHTOTILEIMAGES = "TombstoneTunnels\\client\\assets\\tilemap\\tiles"
PATHTOTESTMAP = "TombstoneTunnels\\client\\assets\\tilemap\\maps\\testmap.csv"

pygame.init()

root = pygame.display.set_mode((1400,800))
mainSurf = pygame.Surface((280,160))

running = True

tileMap = TileMap(16, PATHTOTILEIMAGES, PATHTOTESTMAP, pygame.Vector2(0,0))
ofx=0
ofy=0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == K_d:
            ofx+=10
        elif event.type == pygame.KEYDOWN and event.key == K_a:
            ofx-=10
        
        if event.type == pygame.KEYDOWN and event.key == K_w:
            ofy-=10
        elif event.type == pygame.KEYDOWN and event.key == K_s:
            ofy+=10
    
    tileMap.render(mainSurf, pygame.Vector2(ofx,ofy))

    root.blit(pygame.transform.scale(mainSurf, (1400,800)), (0,0))
    
    pygame.display.flip()
    
    mainSurf.fill((45,45,40))