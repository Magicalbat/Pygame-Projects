import pygame
import json, random

from engine.common import *

class Tilemap:
    def __init__(self, tileSize, chunkSize=8, layers=1):
        self.drawTiles = [{} for i in range(layers)]

        self.chunks = {}
        
        self.chunkSize = chunkSize
        self.tileSize = tileSize
        self.tileImgs = []

        self.imgData = {}
    
    def addDrawTile(self, tilePos, tileIndex, override=False, layer=0):
        #posStr = str(int(tilePos[0])) + ';' + str(int(tilePos[1]))
        if tilePos is not tuple:
            tilePos = (int(tilePos[0]), int(tilePos[1]))
        if tilePos not in self.drawTiles[layer] or override:
            self.drawTiles[layer][tilePos] = tileIndex
    
    def removeDrawTile(self, tilePos, layer=0):
        #posStr = str(int(tilePos[0])) + ';' + str(int(tilePos[1]))
        if tilePos is not tuple:
            tilePos = (int(tilePos[0]), int(tilePos[1]))
        if tilePos in self.drawTiles[layer]:
            self.drawTiles[layer].pop(tilePos)
    
    def generateCollision(self, collidableTiles, optimize, resetCollision=True):
        if resetCollision:
            self.chunks = {}
        collidableTiles = set(collidableTiles)
        self.chunks['tileSize'] = self.tileSize
        self.chunks['chunkSize'] = self.chunkSize
        for l in range(len(self.drawTiles)):
            offset = [0, 0]
            for key, i in self.drawTiles[l].items():
                if key == "offset":
                    offset = i
                else:
                    if i in collidableTiles:
                        #pStr = pStr.split(';')
                        #pos = (int(pStr[0]) * self.tileSize + offset[0], int(pStr[1]) * self.tileSize + offset[1])
                        pos = (key[0] * self.tileSize + offset[0], key[1]* self.tileSize + offset[1])

                        chunkPos = (int(pos[0] / self.chunkSize / self.tileSize), int(pos[1] / self.chunkSize / self.tileSize))

                        if chunkPos not in self.chunks:
                            self.chunks[chunkPos] = []
                        
                        tile = pygame.Rect(pos[0], pos[1], self.tileSize, self.tileSize)
                        
                        self.chunks[chunkPos].append(tile)

        if optimize:
            for pos, chunk in self.chunks.items():
                if pos != 'tileSize' and pos != 'chunkSize':
                    chunk.sort(key=lambda a:(a.x, a.y))
                    self.chunks[pos] = optimizeTilemapCollision(chunk, self.tileSize)
    
    def addDecoration(self, applyTiles, decorationImgs, applyLayer=0, decorationLayer=1, spread=0.1):
        self.tileImgs += decorationImgs

        if len(self.drawTiles) - 1 < decorationLayer:
            self.drawTiles.append({})
        
        self.drawTiles[decorationLayer]["offset"] = (int((self.tileSize - decorationImgs[0].get_width()) / 2), int((self.tileSize - decorationImgs[0].get_height()) / 2))

        for pos, index in self.drawTiles[applyLayer].items():
            if index in applyTiles:
                if random.random() < spread:
                    self.drawTiles[decorationLayer][pos] = len(self.tileImgs) - random.randint(0, len(decorationImgs)) - 1

    def loadTileImgs(self, imgPath, imgTilesDim, imgPadding, tilesCount, colorKey=None):
        if self.imgData == {}:
            self.imgData = {
                'path' : imgPath,
                'tilesDim' : imgTilesDim,
                'padding' : imgPadding,
                'count' : tilesCount,
                'colorKey' : colorKey
            }
        self.tileImgs = loadSpriteSheet(imgPath, (self.tileSize, self.tileSize), imgTilesDim, imgPadding, tilesCount, colorKey)
    
    def loadFromJson(self, path, loadTileImgs=False):
        with open(path) as f:
            data = f.read()
        
        jsonData = json.loads(data)

        if loadTileImgs:
            self.loadTileImgs(jsonData['imgData']['path'], jsonData['imgData']['tilesDim'], jsonData['imgData']['padding'], jsonData['imgData']['count'], jsonData['imgData']['colorKey'])

            jsonData.pop('imgData')
        
        self.tileSize = jsonData['tileSize']
        jsonData.pop('tileSize')
        
        self.drawTiles = []
        for i in range(len(jsonData['drawTiles'])):
            self.drawTiles.append({})
            for key in jsonData['drawTiles'][i].keys():
                splitKey = key.split(';')
                self.drawTiles[i][(int(splitKey[0]), int(splitKey[1]))] = jsonData['drawTiles'][i][key]
        jsonData.pop('drawTiles')

        self.chunks = {
            'tileSize' : jsonData['chunks']['tileSize'],
            'chunkSize' : jsonData['chunks']['chunkSize']
        }
        for key in jsonData['chunks'].keys():
            if key != 'tileSize' and key != 'chunkSize':
                chunk = []
                for tile in jsonData['chunks'][key]:
                    chunk.append(pygame.Rect(tile[0], tile[1], tile[2], tile[3]))
            
                key = key.split(';')
                self.chunks[(int(key[0]), int(key[1]))] = chunk
        jsonData.pop('chunks')

        return jsonData

    def saveToJson(self, path=None, writeFile=True):
        newChunks = {
            'tileSize' : self.chunks['tileSize'],
            'chunkSize' : self.chunks['chunkSize']
        }
        
        for key in self.chunks.keys():
            if key != 'tileSize' and key != 'chunkSize':
                chunk = []
                for rect in self.chunks[key]:
                    chunk.append([rect.x, rect.y, rect.w, rect.h])
                newChunks[f"{int(key[0])};{int(key[1])}"] = chunk
        
        jsonData = {
            'imgData' : self.imgData,
            'tileSize' : self.tileSize,
            'drawTiles' : [],
            'chunks' : newChunks
        }

        for i in range(len(self.drawTiles)):
            jsonData['drawTiles'].append({})
            for key, item in self.drawTiles[i].items():
                jsonData['drawTiles'][i][f"{int(key[0])};{int(key[1])}"] = item
        
        if writeFile and path is not None:
            with open(path, 'w') as f:
                f.write(json.dumps(jsonData, indent=4))
        
        return jsonData
    
    def draw(self, win, scroll=(0,0), highlightLayer=None):
        for l in range(len(self.drawTiles)):
            layerSurf = pygame.Surface((win.get_width(), win.get_height())).convert_alpha()
            layerSurf.set_colorkey((0,0,0))
            offset = [0, 0]
            for key, i in self.drawTiles[l].items():
                if key == "offset":
                    offset = i
                else:
                    #pStr = pStr.split(';')
                    pos = key#(int(pStr[0]) * self.tileSize + offset[0], int(pStr[1]) * self.tileSize + offset[1])

                    if pos[0] * self.tileSize - scroll[0] > -self.tileSize and pos[0] * self.tileSize - scroll[0] < win.get_width() and pos[1] * self.tileSize - scroll[1] > -self.tileSize and pos[1] * self.tileSize - scroll[1] < win.get_height():
                        layerSurf.blit(self.tileImgs[i], (pos[0] * self.tileSize + offset[0] - scroll[0], pos[1] * self.tileSize + offset[1] - scroll[1]))
            if highlightLayer != None and l != highlightLayer:
                layerSurf.set_alpha(255 - ((abs(l - highlightLayer) % len(self.drawTiles) / (len(self.drawTiles) - 1)) * 128 + 64))
            win.blit(layerSurf, (0,0))
    
    def collisionDraw(self, win, drawChunks=False):
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]

        i = 0
        for pos, chunk in self.chunks.items():
            if pos != 'tileSize' and pos != 'chunkSize':
                for tile in chunk:
                    pygame.draw.rect(win, colors[i % len(colors)], tile, width=1)
                    i += 1
        
        if drawChunks:
            for key in self.chunks.keys():
                if key != 'tileSize' and key != 'chunkSize':
                    #pStr = pStr.split(';')
                    pos = key#(int(pStr[0]) * self.tileSize * self.chunkSize, int(pStr[1]) * self.tileSize * self.chunkSize)

                    pygame.draw.rect(win, (0,0,0), (pos[0] * self.tileSize * self.chunkSize, pos[1] * self.tileSize * self.chunkSize, self.chunkSize * self.tileSize, self.chunkSize * self.tileSize), width=1)