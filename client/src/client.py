import random

from client_networking import ClientNetworking
from debug import *
from player import Player
from tilemap import *
from camera import *

PATHTOTILEIMAGES = os.path.join(os.path.dirname(__file__), "..", "assets", "tilemap", "tiles")
PATHTOTESTMAP = os.path.join(os.path.dirname(__file__), "..", "assets", "tilemap", "maps", "testmap.csv")

# pygame init stuff 
pygame.init()

clock = pygame.time.Clock()

# vars
running = True

ofy = 0
ofx = 0

dt = 0  # deltaTime

# class instances
camera = Camera(
    screenSize=pygame.Vector2(1400,1000),
    virtualScrSizeScaler=4,
    position=pygame.Vector2(0,0)
    )

client_networking = ClientNetworking()
# player = Player(client_networking, pygame.Vector2(100, 100))

camera.mode = camera.FOLLOWTARGET
camera.target = player

tileMap = TileMap(16, PATHTOTILEIMAGES, PATHTOTESTMAP, pygame.Vector2(0, 0))
debugger = Debugger()

client_networking.try_login()  # todo login screen / main menu; only do this when the player presses the PLAY button

# noinspection PyTypeChecker
player = None  # our player

while running:
    # events
    events = [event for event in pygame.event.get()]

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            camera.zoom += .1
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            camera.zoom = max(camera.zoom-.1, 1)

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            camera.position.x += 10
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
            camera.position.x -= 10

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            camera.screenshake = not camera.screenshake
            
    # handle available packets from the server
    if not client_networking.tick():
        raise Exception("Disconnected")

    # render other entities
    entities = client_networking.entities
    for entity in entities:
        entity.render(mainSurf)

    player = client_networking.player
    if player is None:
        continue


    # update game logic
    player.update(dt, events)

    # render game
<<<<<<< HEAD
    # tileMap.render(mainSurf, pygame.Vector2(ofx,ofy))
    player.render(mainSurf)

    debugger.debug(f"player position: {round(player.position.x, 3)}, {round(player.position.y, 3)}")
    debugger.debug(f"player velocity: {round(player.velocity.x, 3)}, {round(player.velocity.y, 3)}")
    debugger.debug(f"entity count (without own player): {len(entities)}")
=======
    tileMap.render(camera)
    player.render(camera)
>>>>>>> 0326b33636e264b80028b30da91bd272055ee318

    debugger.debug(int(clock.get_fps()))

    # needs to come last
    camera.update(dt, debugger)
    dt = clock.tick() / 1000

pygame.quit()
