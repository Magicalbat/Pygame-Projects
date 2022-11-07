import pygame
from pygame.math import Vector2

import json, math

class Tilemap:
    def __init__(self, tileSize, imgs, chunkSize=8):
        self.tileSize = tileSize
        self.imgs = imgs
        self.drawTiles = []
        self.chunks = {}
        self.chunkSize = chunkSize

    def toChunkScale(self, p):
        return math.floor(p/self.tileSize/self.chunkSize)

    def toChunkPos(self, p):
        return (self.toChunkScale(p[0]), self.toChunkScale(p[1]))

    def collidePoint(self, p:Vector2):
        cp = self.toChunkPos(p)
        if cp in self.chunks:
            for rect in self.chunks[cp]:
                if rect.collidepoint(p):    return True
        return False

    def _getColRects(self, testPointsX, testPointsY, colRects):
        minX = self.toChunkScale(min(testPointsX))
        maxX = self.toChunkScale(max(testPointsX))

        minY = self.toChunkScale(min(testPointsY))
        maxY = self.toChunkScale(max(testPointsY))

        testChunkPositions = {
            (minX, minY), (minX, maxY),
            (maxX, minY), (maxX, maxY)
        }

        if colRects is None:    colRects = []
        for pos in testChunkPositions:
            if pos in self.chunks:
                colRects += self.chunks[pos]
        return colRects 
    
    def getEntityColRects(self, pos, width, height, vel, colRects=None):
        return self._getColRects( \
            ( pos.x, pos.x + width, pos.x + vel.x, pos.x + width + vel.x ),
            ( pos.y, pos.y + height, pos.y + vel.y, pos.y + height + vel.y ), \
            colRects)

    def getRectColRects(self, rect, colRects=None):
        return self._getColRects((rect.x, rect.right), (rect.y, rect.bottom), colRects)
        
    def draw(self, win, scroll=None):
        if scroll is None:    scroll = Vector2(0, 0)
        winDim = win.get_size()
        for layer in self.drawTiles:
            for tile in layer:
                if tile[0] < winDim[0]+scroll.x and tile[0] > scroll.x-self.tileSize and \
                   tile[1] < winDim[1]+scroll.y and tile[1] > scroll.y-self.tileSize:
                    win.blit(self.imgs[tile[2]], (tile[0] - scroll.x, tile[1] - scroll.y))

    def drawCollision(self, win, scroll=None):
        if scroll is None:    scroll = Vector2(0, 0)
        cols = ((255,0,0), (0,255,0), (0,0,255))
        for pos, rects in self.chunks.items():
            pygame.draw.rect(win, (255,255,255), \
                (pos[0] * self.tileSize * self.chunkSize - scroll.x,\
                 pos[1] * self.tileSize * self.chunkSize - scroll.y,\
                 self.tileSize * self.chunkSize, self.tileSize * self.chunkSize), 1)
            for i, rect in enumerate(rects):
                pygame.draw.rect(win, cols[i%len(cols)], \
                (rect.x - scroll.x, rect.y - scroll.y, \
                 rect.w, rect.h), width=1)

    def loadLevel(self, filepath):
        with open(filepath, 'r') as f:
            data = json.loads(f.read())
        for layer in data["drawTiles"]:
            tempLayer = []
            for key, item in layer.items():
                pStr = key.split(';')
                x, y = int(pStr[0]), int(pStr[1])
                tempLayer.append((x*self.tileSize, y*self.tileSize, item))
            self.drawTiles.append(tempLayer)

        for pos, rects in data["chunks"].items():
            tempRects = []
            for rect in rects:
                tempRects.append(pygame.Rect(rect))
            pStr = pos.split(';')
            self.chunks[(int(pStr[0]), int(pStr[1]))] = tempRects
            
        if "extraData" in data:
            return data["extraData"]