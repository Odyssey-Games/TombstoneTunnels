import pygame, random

class Camera:
    def __init__(self, screenSize:pygame.Vector2, virtualScrSizeScaler:int, position:pygame.Vector2=pygame.Vector2(0,0)):
        self.position = position
        self.display = pygame.display.set_mode(screenSize)
        self.renderTexture = pygame.Surface((int(screenSize.x/virtualScrSizeScaler+1), int(screenSize.y/virtualScrSizeScaler+1)))
        self.zoom = 1
        self.screenshake = False

        self.FREE = 0
        self.FOLLOWTARGET = 1
        self.target = None # entity with .position member var
        self.trackingSpeed = .999
        self.mode = self.FREE

    def update(self, deltaTime, debugger=None):
        self.draw(debugger)
        self.updatePosition(deltaTime)
    
    def updatePosition(self, deltaTime):
        if self.mode == self.FREE:
            pass
        elif self.mode == self.FOLLOWTARGET:
            self.position.x += (self.target.position.x - self.position.x - self.renderTexture.get_width()/2) * self.trackingSpeed * deltaTime 
            self.position.y += (self.target.position.y - self.position.y - self.renderTexture.get_height()/2) * self.trackingSpeed * deltaTime 

    def draw(self, debugger=None):
        dpx = self.display.get_size()[0]
        dpy = self.display.get_size()[1]

        if self.screenshake:
            self.zoom = max(self.zoom, 1.1)

        self.display.blit(
            pygame.transform.scale(
                self.renderTexture, 
                (
                    int(dpx * self.zoom),
                    int(dpy * self.zoom)
                ),
            ), 
            (
                #- ((.5 * self.renderTexture.get_width()*self.zoom) - (.5 * dpx)),
                - int(.5 * (dpx*self.zoom - dpx)) + self.screenshake*(random.randint(-4, 4)),
                - int(.5 * (dpy*self.zoom - dpy)) + self.screenshake*(random.randint(-4, 4))
            )
        )

        if debugger:
            debugger.renderDebug()
        pygame.display.flip()
        self.renderTexture.fill((0,0,0))
        self.display.fill((255,0,0))
    
    def worldToScr(point:pygame.Vector2):
        return point-self.position
        
    def scrToWorld(point:pygame.Vector2):
        return point+self.position
    