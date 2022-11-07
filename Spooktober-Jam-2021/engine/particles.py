import pygame

import random

class Particles:
    def __init__(self, sizeRange, startPosRange, startVelRange=[0, .1, 0, .1], maxParticles=250, circle=False, speed=0.1, gravity=0, colors=None, startCol=(255,255,255), endCol=(0,0,0)):
        self.sizeRange = list(sizeRange)
        self.startPosRange = list(startPosRange)
        self.startVelRange = list(startVelRange)
        self.circle = circle
        self.speed = speed
        self.gravity = gravity
        if colors is None:
            colors = ()
        self.colors = colors
        self.startCol = pygame.Color(startCol)
        self.endCol = pygame.Color(endCol)

        self.pos = []
        self.size = []
        self.vel = []
        self.emptyQueue = []

        for i in range(maxParticles):
            self.pos.append([0,0])
            self.size.append(0)
            self.vel.append([0,0])
            self.emptyQueue.append(i)
        
        self.activeParticles = []
    
    def draw(self, win, scroll=(0,0)):
        for i in self.activeParticles:
            col = (0, 0, 0)
            if self.colors == ():
                col = self.endCol.lerp(self.startCol, self.size[i] / self.sizeRange[1])
            else:
                col = random.choice(self.colors)#self.colors[i % len(self.colors)]

            if self.circle:
                pygame.draw.circle(win, col, (int(self.pos[i][0] - scroll[0]), int(self.pos[i][1] - scroll[1])), int(self.size[i] / 2))
            else:
                pygame.draw.rect(win, col, (int(self.pos[i][0] - self.size[i] / 2 - scroll[0]), int(self.pos[i][1] - self.size[i] / 2 - scroll[1]), int(self.size[i]), int(self.size[i])))
    
    def update(self, delta, tiles=None, colLayer=0, tileSize=8):
        if tiles is None:
            tiles = {}
        #print(self.activeParticles)
        for i in self.activeParticles[::-1]:
            self.vel[i][1] += self.gravity * delta

            self.size[i] -= self.speed * delta

            if tiles != {}:
                self.pos[i][0] += self.vel[i][0] * delta

                tilePos = (int(self.pos[i][0] / tileSize), int(self.pos[i][1] / tileSize))
                if tilePos in tiles[colLayer]:
                    self.vel[i][0] *= -1
                    self.pos[i][0] += self.vel[i][0] * 2 * delta
                
                self.pos[i][1] += self.vel[i][1] * delta

                tilePos = (int(self.pos[i][0] / tileSize), int(self.pos[i][1] / tileSize))
                if tilePos in tiles[colLayer]:
                    self.vel[i][1] *= -random.uniform(0.75, 1)
                    self.pos[i][1] += self.vel[i][1] * 2 * delta
            else:
                self.pos[i][0] += self.vel[i][0] * delta
                self.pos[i][1] += self.vel[i][1] * delta
            
            if self.size[i] < 1:
                self.activeParticles.remove(i)
                self.emptyQueue.append(i)
    
    def emit(self, pos, amount, newVelRange=None):
        if newVelRange is None:
            newVelRange = []
        if amount < 1:
            amount = random.random() < amount
        for i in range(amount):
            if len(self.emptyQueue) > 0:
                self.pos[self.emptyQueue[-1]] = [pos[0] + random.uniform(self.startPosRange[0], self.startPosRange[1]), pos[1] + random.uniform(self.startPosRange[2], self.startPosRange[3])]

                velRange = self.startVelRange
                if newVelRange != []:
                    velRange = newVelRange
                self.vel[self.emptyQueue[-1]] = [random.uniform(velRange[0], velRange[1]), random.uniform(velRange[2], velRange[3])]

                self.size[self.emptyQueue[-1]] = random.uniform(self.sizeRange[0], self.sizeRange[1])

                self.activeParticles.append(self.emptyQueue[-1])
                self.emptyQueue.pop()