import pygame
from pygame.math import Vector2
from src.entities.entity import Entity

class Camera:
    def __init__(self, triggerRects, triggerVectors):
        self.triggerRects = triggerRects
        self.triggerVectors = triggerVectors

        self.scroll = Vector2(0, 0)
        self.bounds = [Vector2(0, 0), Vector2(0, 0)]
        self.targetIndex = 0

        self.prevTarget = -1
        self.changedTarget = False

        self.smoothing = 10

    def scrollRect(self, r):
        return pygame.Rect(r.x - self.scroll.x, r.y - self.scroll.y, r.w, r.h)

    def update(self, e : Entity, winDim):
        self.scroll += ((e.center - Vector2(winDim)*0.5) - self.scroll) / self.smoothing

        col = e.rect.collidelist(self.triggerRects)
        if col > -1:    self.targetIndex = col

        self.changedTarget = False
        if self.prevTarget != -1 and self.prevTarget != self.targetIndex:
            self.changedTarget = True
            
        self.prevTarget = self.targetIndex
        
        if self.smoothing > 1:
            self.bounds[0] = self.bounds[0].lerp(self.triggerVectors[self.targetIndex][0], 0.075)
            self.bounds[1] = self.bounds[1].lerp(self.triggerVectors[self.targetIndex][1], 0.075)
        else:
            self.bounds[0] = self.triggerVectors[self.targetIndex][0]
            self.bounds[1] = self.triggerVectors[self.targetIndex][1]
        
        self.scroll.x = min(self.bounds[1].x-winDim[0], self.scroll.x)
        self.scroll.x = max(self.bounds[0].x, self.scroll.x)
        self.scroll.y = min(self.bounds[1].y-winDim[1], self.scroll.y)
        self.scroll.y = max(self.bounds[0].y, self.scroll.y)

    def snap(self, target, winDim):
        self.scroll = (target - Vector2(winDim)*0.5)