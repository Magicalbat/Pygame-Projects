import pygame
from pygame.math import Vector2

class Projectile:
    def __init__(self, pos, target, r=2, speed=16*6):
        self.pos = pos

        dirVec = target - pos
        self.vel = speed * dirVec.normalize()

        self.r = r
        
    def draw(self, win, scroll):
        pygame.draw.rect(win, (255,255,255), (self.pos.x-self.r-scroll.x, self.pos.y-self.r-scroll.y, self.r+self.r, self.r+self.r))
        
    def update(self, delta):
        self.pos += self.vel * delta