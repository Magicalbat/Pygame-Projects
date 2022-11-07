import pygame
pygame.init()

width = 320
height = 180
win = pygame.display.set_mode((width, height), flags=pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption('Level Editor')

clock = pygame.time.Clock()
fps = 60

import json, time

from engine.common import *
from engine.input import Input
from engine.tilemap import Tilemap

tileSize = 12
tilemap = Tilemap(tileSize, layers=2)
tilemap.loadTileImgs("data/images/tiles/tiles.png", (4,4), (1, 1), 16, (0, 0, 0))

tilemap.loadFromJson("data/maps/level1.json", True)

tileImgs = loadSpriteSheet("data/images/tiles/tiles.png", (12,12), (4,4), (1, 1), 16, (0, 0, 0))

#setCursorFromImg("data/level editor/color picker.png", "X", "data/level editor/color picker.txt")

#setCursorFromTxt("data/level editor/color picker.txt")

sideBarBg = pygame.Surface((tileSize * 7, 180))
sideBarBg.fill((200, 200, 200))
sideBarBg.set_alpha(128)

selectionRects = []

for i in range(len(tileImgs)):
    selectionRects.append(pygame.Rect(tileSize + int(i / 7) * tileSize * 2, tileSize * i * 2 + tileSize * 2 - (int(i / 7) * tileSize * 14), tileSize, tileSize))

selectedTile = 0

mouseBox = pygame.Surface((tileSize, tileSize))
mouseBox.set_colorkey((0,0,0))
pygame.draw.rect(mouseBox, (255, 0, 0), (0, 0, tileSize, tileSize), width=1)
mouseBox.set_alpha(128)

font = pygame.font.SysFont('comicsans', 16)
currentLayer = 0

editState = "Pencil"

selectionPos1 = selectionPos2 = [0, 0]

def changeState(newState):
    global editState
    editState = newState

    if newState == "Pencil":
        setCursorFromTxt("levelEditor/data/pencil.txt")
    elif newState == "Box Select":
        setCursorFromTxt("levelEditor/data/box select.txt")
    elif newState == "Bucket":
        setCursorFromTxt("levelEditor/data/bucket.txt")
    elif newState == "Color Picker":
        setCursorFromTxt("levelEditor/data/color picker.txt")

changeState("Pencil")
inp = Input()
trueScroll = scroll = [0,0]

mainRunning = True
while mainRunning:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainRunning = False

    inp.update()
    
    if inp.keyJustPressed(pygame.K_SPACE):
        currentLayer += 1
        currentLayer %= len(tilemap.drawTiles)

    if inp.keyJustPressed(pygame.K_e):
        changeState("Box Select")
    if inp.keyJustPressed(pygame.K_p):
        changeState("Pencil")
    if inp.keyJustPressed(pygame.K_b):
        changeState("Bucket")
    if inp.keyJustPressed(pygame.K_i):
        changeState("Color Picker")
    
    win.fill((0, 0, 128))

    if inp.keyDown(pygame.K_a):
        trueScroll[0] -= 32 * clock.get_time() / 1000
    if inp.keyDown(pygame.K_d):
        trueScroll[0] += 32 * clock.get_time() / 1000
    if inp.keyDown(pygame.K_w):
        trueScroll[1] -= 32 * clock.get_time() / 1000
    if inp.keyDown(pygame.K_s):
        trueScroll[1] += 32 * clock.get_time() / 1000

    scroll = [int(trueScroll[0] / tileSize) * tileSize, int(trueScroll[1] / tileSize) * tileSize]

    tilemap.draw(win, scroll)#, currentLayer)
    #tilemap.collisionDraw(win, True)

    mousePos = pygame.mouse.get_pos()
    mousePos = list(mousePos)

    mousePos[0] = int((mousePos[0] + scroll[0]) / tileSize) * tileSize
    mousePos[1] = int((mousePos[1] + scroll[1]) / tileSize) * tileSize

    mouseRect = pygame.Rect(mousePos[0], mousePos[1], tileSize, tileSize)

    if mousePos[0] - scroll[0] <= sideBarBg.get_width() and inp.mouseJustPressed(0):
            for i in range(len(selectionRects)):
                if pygame.Rect(mouseRect.x - scroll[0], mouseRect.y - scroll[1], mouseRect.w, mouseRect.h).colliderect(selectionRects[i]):
                    selectedTile = i
    else:
        if editState == "Pencil":
            win.blit(mouseBox, (mousePos[0] - scroll[0], mousePos[1] - scroll[1]))
            #pygame.draw.rect(win, (255, 0, 0), (mousePos[0],   mousePos[1], tileSize, tileSize), width=1)
    
            if mousePos[0] - scroll[0] >= sideBarBg.get_width():
                if inp.mouseDown(0) or inp.keyDown(pygame.K_v):
                    tilemap.addDrawTile((mousePos[0] / tileSize, mousePos[1] / tileSize),   selectedTile, True, currentLayer)
            
                if inp.mouseDown(2) or inp.keyDown(pygame.K_x):
                    tilemap.removeDrawTile((mousePos[0] /   tileSize, mousePos[1] / tileSize), currentLayer)
            
            #if inp.mouseJustPressed(1) or inp.keyJustPressed(pygame.K_z):
            #    selectedTile += 1
            #    selectedTile %= len(tileImgs)
    
        elif editState == "Box Select":
            boxDim = (selectionPos2[0] - selectionPos1[0],   selectionPos2[1] - selectionPos1[1])
            selectionBox = pygame.Rect(min(selectionPos1[0], selectionPos2[0]), min(selectionPos1[1], selectionPos2[1]), abs(boxDim[0]), abs(boxDim[1]))
    
            if inp.mouseJustPressed(0):
                selectionPos1 = mousePos
            
            if inp.mouseDown(0) and mousePos[0] - scroll[0] > sideBarBg.get_width():
                selectionPos2 = mousePos
            
            if inp.keyJustPressed(pygame.K_f):
                for y in range(int(selectionBox.h / tileSize))  :
                    for x in range(int(selectionBox.w /     tileSize)):
                        tilemap.addDrawTile((x +    selectionBox.x / tileSize, y +     selectionBox.y / tileSize),     selectedTile, True, currentLayer)
            
            if inp.keyJustPressed(pygame.K_x):
                for y in range(int(selectionBox.h / tileSize))  :
                    for x in range(int(selectionBox.w /     tileSize)):
                        tilemap.removeDrawTile((x +     selectionBox.x / tileSize, y +  selectionBox.y / tileSize), currentLayer)
    
            pygame.draw.rect(win, (255, 255, 255),  (selectionBox.x - scroll[0], selectionBox.y - scroll[1], selectionBox.w, selectionBox.h), width=1)
        elif editState == "Bucket":
            if inp.mouseJustPressed(0):
                floodFill(tilemap.drawTiles[currentLayer], (int(mousePos   [0] / tileSize), int(mousePos[1] / tileSize)),  selectedTile)
        elif editState == "Color Picker":
            win.blit(mouseBox, (mousePos[0] - scroll[0], mousePos[1] - scroll[1]))

            if inp.mouseJustPressed(0):
                if (int(mousePos[0] / tileSize), int(mousePos[1] / tileSize)) in tilemap.drawTiles[currentLayer]:
                    selectedTile = tilemap.drawTiles[currentLayer][(int(mousePos[0] / tileSize), int(mousePos[1] / tileSize))]
                    changeState("Pencil")
    
    win.blit(sideBarBg, (0,0))

    for i in range(len(tileImgs)):
        win.blit(tileImgs[i], (selectionRects[i].x, selectionRects[i].y))
     
    win.blit(tileImgs[selectedTile], (0,0))
    win.blit(font.render(f"{currentLayer}", False, (255,255,255)), (16, 0))

    pygame.display.update()

tilemap.generateCollision({i + 1 for i in range(15)}, True)
tilemapData = tilemap.saveToJson("data/maps/test.json", False)

print("Click on player spawn :)")

mousePos = pygame.mouse.get_pos()
mousePos = list(mousePos)

mousePos[0] = int((mousePos[0] + scroll[0]) / tileSize)# * tileSize
mousePos[1] = int((mousePos[1] + scroll[1]) / tileSize)# * tileSize
#(int(mousePos[0] / tileSize), int(mousePos[1] / tileSize))

while not inp.mouseJustPressed(0):
    mousePos = pygame.mouse.get_pos()
    mousePos = list(mousePos)

    mousePos[0] = int((mousePos[0] + scroll[0]) / tileSize) * tileSize
    mousePos[1] = int((mousePos[1] + scroll[1]) / tileSize) * tileSize

    for event in pygame.event.get():
        pass

    inp.update()

tilemapData['playerSpawn'] = mousePos

print("Click on level exit :))))))))")

time.sleep(0.5)
inp.update()
inp.update()

mousePos = pygame.mouse.get_pos()
mousePos = list(mousePos)

mousePos[0] = int((mousePos[0] + scroll[0]) / tileSize)# * tileSize
mousePos[1] = int((mousePos[1] + scroll[1]) / tileSize)# * tileSize
#(int(mousePos[0] / tileSize), int(mousePos[1] / tileSize))

while not inp.mouseJustPressed(0):
    mousePos = pygame.mouse.get_pos()
    mousePos = list(mousePos)

    mousePos[0] = int((mousePos[0] + scroll[0]) / tileSize) * tileSize
    mousePos[1] = int((mousePos[1] + scroll[1]) / tileSize) * tileSize

    for event in pygame.event.get():
        pass

    inp.update()

tilemapData['levelExit'] = mousePos

if False:
    with open("data/maps/level1.json", 'w') as f:
        f.write(json.dumps(tilemapData, indent=4))

pygame.quit()