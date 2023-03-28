from debug import *
from player import *
from tilemap import *

PATHTOTILEIMAGES = os.path.join(os.path.dirname(__file__), "..", "assets", "tilemap", "tiles")
PATHTOTESTMAP = os.path.join(os.path.dirname(__file__), "..", "assets", "tilemap", "maps", "testmap.csv")

# pygame init stuff 
pygame.init()

root = pygame.display.set_mode((1400, 800))
mainSurf = pygame.Surface((280, 160))

clock = pygame.time.Clock()

# vars
running = True

ofy = 0
ofx = 0

dt = 0  # deltaTime

# class instances
tileMap = TileMap(16, PATHTOTILEIMAGES, PATHTOTESTMAP, pygame.Vector2(0, 0))
debugger = Debugger()
player = Player(pygame.Vector2(100, 100))

while running:
    # events
    events = [event for event in pygame.event.get()]

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # update game logic
    player.update(dt, events)

    # render game
    # tileMap.render(mainSurf, pygame.Vector2(ofx,ofy))
    player.render(mainSurf)

    debugger.debug(f"player position: {round(player.position.x, 3)}, {round(player.position.y, 3)}")
    debugger.debug(f"player velocity: {round(player.velocity.x, 3)}, {round(player.velocity.y, 3)}")

    debugger.debug(int(clock.get_fps()))

    # boilerplate
    root.blit(pygame.transform.scale(mainSurf, (1400, 800)), (0, 0))
    debugger.renderDebug()
    pygame.display.flip()

    mainSurf.fill((45, 45, 40))

    dt = clock.tick() / 1000

pygame.quit()
