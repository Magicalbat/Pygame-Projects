import pygame

import math, copy

from engine.common import *

class Entity:
    def __init__(self, x, y, width, height, rectCol=(0,255,0)):
        self.rect = pygame.Rect((copy.deepcopy(x), copy.deepcopy(y), copy.deepcopy(width), copy.deepcopy(height)))
        self.pos = pygame.math.Vector2((copy.deepcopy(x), copy.deepcopy(y)))

        self.rectDisplaySurf = pygame.Surface((width, height))
        self.rectDisplaySurf.fill(rectCol)
        self.rectDisplaySurf.set_alpha(128)

        self.applyGravity = False
        self.applyVelocity = False
        self.handleCollision = False

        self.gravity = 320
        self.velocity = pygame.math.Vector2((0,0))

        self.collisionTypes = {'top': False, 'bottom': False, 'right': False, 'left': False}

    def drawRect(self, win, scroll=(0,0)):
        win.blit(self.rectDisplaySurf, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        #pygame.draw.rect(win, (255,0,0), (self.rect.x - scroll[0], self.rect.y - scroll[1], self.rect.w, self.rect.h), width=1)

    def addChunk(self, pos, chunks, collisionRects):
        self.addChunkFromChunkPos((self.toChunkSpace(pos[0], chunks), self.toChunkSpace(pos[1], chunks)), chunks, collisionRects)
    
    def addChunkFromChunkPos(self, pos, chunks, collisionRects):
        pos = (int(pos[0]), int(pos[1]))
        if pos in chunks:
            collisionRects += chunks[pos]
    
    def toChunkSpace(self, num, chunks):
        return int(num / chunks['chunkSize'] / chunks['tileSize'])
    
    def getChunksWithMove(self, move, chunks, collisionRects):
        # Assumes that entity will not move enough to skip a chunk
        testPointsX = [
            self.pos.x,
            self.pos.x + self.rect.w,
            self.pos.x + move.x,
            self.pos.x + self.rect.w + move.x
        ]

        minX = min(testPointsX)
        maxX = max(testPointsX)

        testPointsY = [
            self.pos.y,
            self.pos.y + self.rect.h,
            self.pos.y + move.y,
            self.pos.y + self.rect.h + move.y
        ]

        minY = min(testPointsY)
        maxY = max(testPointsY)

        testChunks = [
            (self.toChunkSpace(minX, chunks), self.toChunkSpace(minY, chunks)),
            (self.toChunkSpace(maxX, chunks), self.toChunkSpace(minY, chunks)),
            (self.toChunkSpace(maxX, chunks), self.toChunkSpace(maxY, chunks)),
            (self.toChunkSpace(minX, chunks), self.toChunkSpace(maxY, chunks))
        ]

        testChunks = list(set(testChunks))

        for chunk in testChunks:
            self.addChunkFromChunkPos(chunk, chunks, collisionRects)

    def updateRect(self):
        if self.velocity.x > 0:
            self.rect.x = math.ceil(self.pos.x)
        else:
            self.rect.x = int(self.pos.x)
        
        if self.velocity.y > 0:
            self.rect.y = math.ceil(self.pos.y)
        else:
            self.rect.y = int(self.pos.y)

    def update(self, delta, collisionRects=None, chunks=None):
        if collisionRects is None:
            collisionRects = []
        if chunks is None:
            chunks = {}
        if self.applyGravity:
            self.velocity.y += self.gravity * delta

        if self.applyVelocity and not self.handleCollision:
            self.pos.x += self.velocity.x * delta
            
            self.pos.y += self.velocity.y * delta

            self.updateRect()

        if self.handleCollision:
            self.collisionTypes = {'top': False, 'bottom': False, 'right': False, 'left': False}

            if chunks != {}:
                self.getChunksWithMove(self.velocity * delta, chunks, collisionRects)

            self.pos.x += self.velocity.x * delta
            self.updateRect()

            hitlist = getCollidingRects(self.rect, collisionRects)

            for rect in hitlist:
                if self.velocity.x > 0:
                    self.rect.right = rect.left
                    self.pos.x = self.rect.x
                    self.velocity.x = 0
                    self.collisionTypes['right'] = True
                if self.velocity[0] < 0:
                    self.rect.left = rect.right
                    self.pos.x = self.rect.x
                    self.velocity.x = 0
                    self.collisionTypes['left'] = True
            
            self.pos.y += self.velocity.y * delta
            self.updateRect()

            hitlist = getCollidingRects(self.rect, collisionRects)

            for rect in hitlist:
                if self.velocity.y > 0 and self.collisionTypes['top'] == False:
                    self.rect.bottom = rect.top
                    self.pos.y = self.rect.y
                    self.velocity.y = 0
                    self.collisionTypes['bottom'] = True
                elif self.velocity.y < 0:
                    self.rect.top = rect.bottom
                    self.pos.y = self.rect.y
                    self.velocity.y = 1
                    self.collisionTypes['top'] = True
