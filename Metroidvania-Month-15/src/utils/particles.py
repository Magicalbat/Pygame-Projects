import pygame
from pygame.math import Vector2

import random

class Particles:
    def __init__(self, sizeRange, posRange, circle=False, speed=10, accel=Vector2(0, 0), collision=False, colors=None):
        self.sizeRange, self.posRange = sizeRange, posRange
        self.circle, self.speed, self.accel, self.collision = circle, speed, accel, collision
        if colors is None:    self.colors = [(255,255,255)]
        else:    self.colors = tuple(colors)

        # Data for particles
        self.pos = []
        self.siz = [] # Radius
        self.vel = []
        self.col = []

    def draw(self, win, scroll=Vector2(0, 0)):
        if self.circle:
            for i in range(len(self.pos)):
                pygame.draw.circle(win, self.colors[self.col[i]], self.pos[i]-scroll, self.siz[i])
        else:
            for i in range(len(self.pos)):
                pygame.draw.rect(win, self.colors[self.col[i]], \
                    (self.pos[i].x - self.siz[i] - scroll.x, \
                     self.pos[i].y - self.siz[i] - scroll.y, \
                     self.siz[i] * 2, self.siz[i] * 2))

    def update(self, delta, tilemap=None, colRects=None):
        if colRects is None:    colRects = []
        for i in range(len(self.pos))[::-1]:
            self.vel[i] += self.accel * delta

            if self.collision:
                self.pos[i].x += self.vel[i].x * delta
                if tilemap.collidePoint(self.pos[i]) or \
                    any([rect.collidepoint(self.pos[i]) for rect in colRects]):
                    self.vel[i].x *= -1
                    self.pos[i].x += self.vel[i].x * 2 * delta
                    
                self.pos[i].y += self.vel[i].y * delta
                if tilemap.collidePoint(self.pos[i]):
                    self.vel[i].y *= -random.uniform(0.75, 1)
                    self.pos[i].y += self.vel[i].y * 2 * delta
            else:
                self.pos[i] += self.vel[i] * delta

            self.siz[i] -= self.speed * delta

            if self.siz[i] < 1:
                self.pos.pop(i)
                self.siz.pop(i)
                self.vel.pop(i)
                self.col.pop(i)

    def emit(self, pos, amount, velRange):
        num = amount if amount >= 1 else random.random() > amount
        for i in range(num):
            self.pos.append(pos + Vector2(random.uniform(*self.posRange[:2]), random.uniform(*self.posRange[2:])))
            self.siz.append(random.uniform(*self.sizeRange))
            self.vel.append(Vector2(random.uniform(*velRange[:2]), random.uniform(*velRange[2:])))
            self.col.append(random.randrange(0, len(self.colors)))
    
    def clear(self):
        while len(self.pos):
            self.pos.pop()
            self.siz.pop()
            self.vel.pop()
            self.col.pop()

    def collideRect(self, rect):
        for pos in self.pos:
            if rect.collidepoint(pos):    return True
        return False