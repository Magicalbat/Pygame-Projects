import pygame
from pygame.math import Vector2

import random, copy

from src.utils.particles import Particles

class SpecialTileManager:
    def __init__(self, extraData, tileSize=16):
        if "Fire" in extraData: self.fireManager = FireManager(extraData["Fire"])
        else: self.fireManager = FireManager([])

        if "SlimeMold" in extraData: self.slimeManager = SlimeManager(extraData["SlimeMold"])
        else: self.slimeManager = SlimeManager([])
        
        if "Acid" in extraData: self.acidManager = AcidManager(extraData["Acid"])
        else: self.acidManager = AcidManager([])

        self.reset = False

    def getColRects(self):
        return self.slimeManager.rects

    def setup(self):
        self.fireManager.setup()
        self.slimeManager.setup()
        self.acidManager.setup()

        self.reset = False

    def draw(self, win, scroll):
        self.fireManager.draw(win, scroll)
        self.slimeManager.draw(win, scroll)
        self.acidManager.draw(win, scroll)

    def update(self, delta, player):
        self.fireManager.update(delta, player)
        self.slimeManager.update(delta, player)
        self.acidManager.update(delta, player)

        self.reset = not player.invincible and (self.fireManager.reset or self.slimeManager.reset or self.acidManager.reset)

class AcidManager:
    def __init__(self, positions, tileSize=16):
        self.rects = [pygame.Rect(pos[0], pos[1], tileSize, tileSize) for pos in positions]

    def setup(self):
        self.reset = False

    def draw(self, win, scroll):
        for r in self.rects:
            pygame.draw.rect(win, (116, 255, 82), (r.topleft-scroll, (r.w, r.h)))

    def update(self, delta, player):
        if player.rect.collidelist(self.rects) != -1:
            self.reset = True

class SlimeManager:
    def __init__(self, positions, tileSize=16):
        self.origRects = [pygame.Rect(pos[0], pos[1], tileSize, tileSize) for pos in positions]
        self.tileSize = tileSize

        self.colors = (
            (224, 66, 245), (192, 43, 255), (240, 140, 255), (155, 99, 230)
        )

        self.setup()

    def setup(self):
        self.rects = copy.deepcopy(self.origRects)
        self.sides = [self.tileSize for _ in self.rects]
        
        self.reset = False

    def rectHash(self, r):
        return hash(r.x) ^ hash(r.y)>>1 ^ hash(r.w)>>2 ^ hash(r.h)>>3

    def randCol(self, r):
        random.seed(self.rectHash(r))
        i = random.randrange(0,len(self.colors))
        random.seed()
        return self.colors[i]

    def draw(self, win, scroll):
        for i, r in enumerate(self.rects):
            pygame.draw.rect(win, self.randCol(r), (r.center-scroll-Vector2(self.sides[i]*0.5, self.sides[i]*0.5), (self.sides[i], self.sides[i])))
            
    def update(self, delta, player):
        if player.acid:
            for i in range(len(self.rects))[::-1]:
                if player.waterParticles.collideRect(self.rects[i]):
                    self.sides[i] -= 0.5
                    if self.sides[i] <= 2:
                        self.rects.pop(i)
                        self.sides.pop(i)

class FireManager:
    def __init__(self, positions, tileSize=16):
        self.rects = [pygame.Rect(pos[0], pos[1], tileSize, tileSize) for pos in positions]


    def setup(self):
        self.particles = Particles((3,5), (0,16, -2,2), colors=[
            (255,128,0), (255,255,0), (255,0,0), (255,255,255)
        ])
        
        self.activeTimers = [0 for _ in self.rects]
        self.reset = False

    def draw(self, win, scroll):
        self.particles.draw(win, scroll)

    def update(self, delta, player):
        self.particles.update(delta)
        
        for i, r in enumerate(self.rects):
            if player.waterParticles.collideRect(r):
                self.activeTimers[i] = 2
            elif self.activeTimers[i] <= 0 and player.rect.colliderect(r):
                self.reset = True
            
            if self.activeTimers[i] <= 0.3:
                self.particles.emit(r.bottomleft, 0.25, (-20,20, -50,-100))
            if self.activeTimers[i] > 0:
                self.activeTimers[i] -= delta