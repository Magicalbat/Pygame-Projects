import pygame

import copy

from engine.entity import Entity
from engine.particles import Particles

class Pumpkin(Entity):
    def __init__(self, x, y, width, height, startVel, gravity, img, jackImg):
        super().__init__(x, y, width, height, (0,255,0))

        self.velocity = copy.deepcopy(startVel)
        self.gravity = copy.deepcopy(gravity)

        self.applyGravity = True
        self.handleCollision = True
        self.applyVelocity = True

        self.stopping = False

        self.img = img
        self.jackOLanternImg = jackImg
        
        self.jackOLantern = False

        self.fireParticles = Particles([6, 8], [-4, 4, -1, 1], [-15, 15, -35, -40], 100, True, 8, 125, ((250, 192, 0), (255, 117, 0), (255,255,0), (255,128,0)))
    
    def changeToJackOLantern(self):
        self.img = self.jackOLanternImg
        self.jackOLantern = True

    def draw(self, win, scroll=(0,0)):
        #super().drawRect(win, scroll)
        if self.jackOLantern:
            self.fireParticles.draw(win, scroll)

        win.blit(self.img, (self.rect.x - scroll[0] - 1, self.rect.y - scroll[1] - 2))
    
    def update(self, delta, collisionRects=None, chunks=None):
        if self.handleCollision:
            rects = copy.deepcopy(collisionRects)
            if self.rect in collisionRects:
                rects.remove(self.rect)
            super().update(delta, rects, chunks)

            self.velocity.y = min(self.velocity.y, self.gravity * 0.75)

            if self.velocity.y == 0:
                self.stopping = True

                self.applyGravity = False
                self.handleCollision = False

                self.velocity.x = 0
                self.velocity.y = 0
        else:
            self.velocity.x = 0
            self.velocity.y = 0
        
        if self.jackOLantern:
            self.fireParticles.update(delta)

            self.fireParticles.emit((self.pos.x + 6, self.pos.y + 8), .25)