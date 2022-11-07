import pygame

pygame.init()

pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEWHEEL])

width = int(320 * 1.5)
height = int(180 * 1.5)
screen = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE, 16)
pygame.display.set_caption("Level Editor V2")

clock = pygame.time.Clock()
fps = 60

import enum, json, os

from engine.common import *
from engine.input import Input
from engine.tilemap import Tilemap
from engine.text import Text

class States(enum.Enum):
    PENCIL = enum.auto(),
    BOX_SELECT = enum.auto(),
    BUCKET = enum.auto(),
    COLOR_PICKER = enum.auto()

    EXTRA_DATA = enum.auto()

def changeCursor(cursorState):
    if changeCursor:
        if cursorState == States.PENCIL:
            setCursorFromTxt("data/levelEditor/pencil.txt")
        elif cursorState == States.BOX_SELECT:
            setCursorFromTxt("data/levelEditor/box select.txt")
        elif cursorState == States.BUCKET:
            setCursorFromTxt("data/levelEditor/bucket.txt")
        elif cursorState == States.COLOR_PICKER:
            setCursorFromTxt("data/levelEditor/color picker.txt")
        elif cursorState == States.EXTRA_DATA:
            pygame.mouse.set_cursor(pygame.cursors.arrow)

levelNum = 15

tileSize = 12
tilemap = Tilemap(tileSize, layers=2)
tilemap.loadTileImgs("data/images/tiles/tiles.png", (4,4), (1, 1), 16, (0, 0, 0))

loadedExtraData = {}
if os.path.exists(f"data/maps/level{levelNum}.json"):
    loadedExtraData = tilemap.loadFromJson(f"data/maps/level{levelNum}.json", True)

currentLayer = 0
editState = States.PENCIL
changeCursor(States.PENCIL)
selectedTile = 0

selectionTilePos1 = selectionTilePos2 = [0,0]

def getSelectionTileRect():
    tileRect = pygame.Rect((0,0,0,0))
        
    if selectionTilePos1[0] < selectionTilePos2[0]:
        tileRect.x = selectionTilePos1[0]
        tileRect.w = selectionTilePos2[0] - selectionTilePos1[0] + 1
    else:
        tileRect.x = selectionTilePos2[0]
        tileRect.w = selectionTilePos1[0] - selectionTilePos2[0] + 1
    
    if selectionTilePos1[1] < selectionTilePos2[1]:
        tileRect.y = selectionTilePos1[1]
        tileRect.h = selectionTilePos2[1] - selectionTilePos1[1] + 1
    else:
        tileRect.y = selectionTilePos2[1]
        tileRect.h = selectionTilePos1[1] - selectionTilePos2[1] + 1
    
    return tileRect

text = Text()
text.loadFontImg("data/images/text.png")#, scale=(2,2))

tileImgs = loadSpriteSheet("data/images/tiles/tiles.png", (12,12), (4,4), (1, 1), 16, (0, 0, 0))

extraDataKeys = ['playerSpawn', 'levelExit', 'maxPumpkins', 'spikes', 'wind', 'cameraBounds', 'text']
extraData = {key : [] for key in extraDataKeys}

textData = ""

for key, value in loadedExtraData.items():
    if key in extraData:
        if key == 'maxPumpkins':
            extraData[key] = [[value * tileSize, 0]]
        elif all((not isinstance(i, str) for i in value)):
            extraData[key] = list(value)
        else:
            for i in value:
                if isinstance(i, str):
                    textData = i

extraDataImgs = []
extraDataAlphaImgs = []
colors = [(255,0,0), (255, 255, 0), (255, 0, 255), (0,255,0), (255,255,0), (0,255,255), (0,0,255), (255,0,255), (0,255,255)]

selectedExtraData = 0

for i, key in enumerate(extraDataKeys):
    img = pygame.Surface((tileSize, tileSize)).convert()
    img.fill(colors[i % len(colors)])

    img.blit(text.createTextSurf(key[0].upper()), (0,0))

    extraDataImgs.append(img.copy())

    img.set_alpha(128)

    extraDataAlphaImgs.append(img.copy())

sbWidth = int(tileSize * 5) # sidebar width
sidebar = pygame.Surface((sbWidth, height))

sbScroll = tileSize * 4
sbScrollSpeed = tileSize
sbTileRects = [pygame.Rect((tileSize + (2 * tileSize * (i % 2)), sbScroll + ((i // 2) * 2 * tileSize), tileSize, tileSize)) for i in range(len(tileImgs))]

win = pygame.Surface((width - sbWidth, height))

fScroll = [0,0]
scrollSpeed = tileSize * 10

inp = Input()

running = True
while running:
    clock.tick(fps)
    delta = clock.get_time() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEWHEEL:
            if mousePos[0] < sbWidth:
                sbScroll += sbScrollSpeed * event.y

                sbTileRects = [pygame.Rect((tileSize + (2 * tileSize * (i % 2)), sbScroll + ((i // 2) * 2 * tileSize), tileSize, tileSize)) for i in range(len(tileImgs))]

    inp.update()

    if inp.keyJustPressed(pygame.K_F11):
        pygame.display.toggle_fullscreen()

    # CHANGE EDIT STATES ===============================
    if inp.keyJustPressed(pygame.K_p):
        editState = States.PENCIL
        changeCursor(States.PENCIL)
    if inp.keyJustPressed(pygame.K_e):
        editState = States.BOX_SELECT
        changeCursor(States.BOX_SELECT)
    if inp.keyJustPressed(pygame.K_b):
        editState = States.BUCKET
        changeCursor(States.BUCKET)
    if inp.keyJustPressed(pygame.K_k):
        editState = States.COLOR_PICKER
        changeCursor(States.COLOR_PICKER)
    
    if inp.keyJustPressed(pygame.K_BACKQUOTE):
        editState = States.EXTRA_DATA
        changeCursor(States.EXTRA_DATA)
    
    if inp.keyJustPressed(pygame.K_SPACE):
        currentLayer += 1
        currentLayer %= len(tilemap.drawTiles)
    
    # CAMERA MOVEMENT ===================================
    if inp.keyDown(pygame.K_w):
        fScroll[1] -= scrollSpeed * delta
    if inp.keyDown(pygame.K_a):
        fScroll[0] -= scrollSpeed * delta
    if inp.keyDown(pygame.K_s):
        fScroll[1] += scrollSpeed * delta
    if inp.keyDown(pygame.K_d):
        fScroll[0] += scrollSpeed * delta
    
    if inp.keyJustPressed(pygame.K_PERIOD):
        fScroll = [0,0]
    
    scroll = (int(fScroll[0]), int(fScroll[1]))
    
    mousePos = pygame.mouse.get_pos()
    tileMousePos = ((mousePos[0] - sbWidth) // tileSize, mousePos[1] // tileSize)
    scrolledTileMousePos = ((mousePos[0] - sbWidth + scroll[0]) // tileSize, (mousePos[1] + scroll[1]) // tileSize)
    drawMousePos = ((scrolledTileMousePos[0] * tileSize) - scroll[0], (scrolledTileMousePos[1] * tileSize) - scroll[1])

    if mousePos[0] < sbWidth: # SIDEBAR LOGIC ==========
        if inp.mouseJustPressed(0):
            for i in range(len(sbTileRects)):
                if sbTileRects[i].collidepoint(mousePos):
                    selectedTile = i
                    break
    else: # WIN LOGIC =================================
        if editState == States.PENCIL:
            if inp.mouseDown(0):
                tilemap.addDrawTile(scrolledTileMousePos, selectedTile, True, currentLayer)
            elif inp.mouseDown(2) or inp.keyDown(pygame.K_x):
                tilemap.removeDrawTile(scrolledTileMousePos, currentLayer)
        elif editState == States.BOX_SELECT:
            if inp.mouseJustPressed(0):
                selectionTilePos1 = scrolledTileMousePos
            
            if inp.mouseDown(0):
                selectionTilePos2 = scrolledTileMousePos
            
            if inp.keyJustPressed(pygame.K_f):
                tileRect = getSelectionTileRect()

                for x in range(tileRect.w):
                    for y in range(tileRect.h):
                        tilemap.addDrawTile((tileRect.x + x, tileRect.y + y), selectedTile, True, currentLayer)
            
            if inp.keyJustPressed(pygame.K_x):
                tileRect = getSelectionTileRect()

                for x in range(tileRect.w):
                    for y in range(tileRect.h):
                        tilemap.removeDrawTile((tileRect.x + x, tileRect.y + y), currentLayer)
            
        elif editState == States.BUCKET:
            if inp.mouseJustPressed(0):
                floodFill(tilemap.drawTiles[currentLayer], scrolledTileMousePos, selectedTile)
        elif editState == States.COLOR_PICKER:
            if inp.mouseJustPressed(0):
                if scrolledTileMousePos in tilemap.drawTiles[currentLayer]:
                    selectedTile = tilemap.drawTiles[currentLayer][scrolledTileMousePos]
                    
                    editState = States.PENCIL
                    changeCursor(States.PENCIL)
        elif editState == States.EXTRA_DATA:
            if inp.mouseDown(0):
                dataPos = (scrolledTileMousePos[0] * tileSize, scrolledTileMousePos[1] * tileSize)
                if dataPos not in extraData[extraDataKeys[selectedExtraData]]: 
                    extraData[extraDataKeys[selectedExtraData]].append(dataPos)
            if inp.mouseJustPressed(1) or inp.keyJustPressed(pygame.K_c):
                selectedExtraData += 1
                selectedExtraData %= len(extraDataKeys)
            if inp.mouseDown(2) or inp.keyDown(pygame.K_x):
                extraData[extraDataKeys[selectedExtraData]] = [i for i in extraData[extraDataKeys[selectedExtraData]] if tuple(i) != (scrolledTileMousePos[0] * tileSize, scrolledTileMousePos[1] * tileSize)]

    # WIN DRAW =========================================
    win.fill((200,200,200))

    tilemap.draw(win, scroll)#, currentLayer)

    if editState == States.PENCIL:
        pass#win.blit(tileImgs[selectedTile], (drawMousePos[0], drawMousePos[1]))
    elif editState == States.BOX_SELECT:
        tileRect = getSelectionTileRect()
        
        pygame.draw.rect(win, (255,255,255), ((tileRect.x * tileSize) - scroll[0], (tileRect.y * tileSize) - scroll[1], tileRect.w * tileSize, tileRect.h * tileSize), width=1)
    elif editState == States.EXTRA_DATA:
        win.blit(extraDataAlphaImgs[selectedExtraData], (drawMousePos[0], drawMousePos[1]))
    
    for i in range(len(extraDataKeys)):
        for j in range(len(extraData[extraDataKeys[i]])):
            drawPos = (extraData[extraDataKeys[i]][j][0] - scroll[0], extraData[extraDataKeys[i]][j][1] - scroll[1])
            win.blit(extraDataAlphaImgs[i], drawPos)

            if extraDataKeys[i] == 'cameraBounds':
                pygame.draw.rect(win, (0,255,0), (drawPos[0], drawPos[1], 320, 180), width=1)

    if editState != States.BOX_SELECT and editState != States.EXTRA_DATA:
        pygame.draw.rect(win, (0,245,255), (drawMousePos[0] - 1, drawMousePos[1] - 1, tileSize+2, tileSize+2), width=1)

    # SIDEBAR DRAW =====================================
    sidebar.fill((50,50,75))

    for i in range(len(tileImgs)):
        sidebar.blit(tileImgs[i], (tileSize + (2 * tileSize * (i % 2)), sbScroll + ((i // 2) * 2 * tileSize)))
    
    sRect = sbTileRects[selectedTile] # Selected Rect
    pygame.draw.rect(sidebar, (0,245,255), (sRect.x - 1, sRect.y - 1, sRect.w + 2, sRect.h + 2), width=1)

    pygame.draw.rect(sidebar, (50,50,75), (0,0,sbWidth,30))

    sidebar.blit(text.createTextSurf(f"Layer: {currentLayer}"), (0,0))
    sidebar.blit(text.createTextSurf(f"({int(mousePos[0])}, {int(mousePos[1])})"), (0,9))
    sidebar.blit(text.createTextSurf(f"({int(scrolledTileMousePos[0])}, {int(scrolledTileMousePos[1])})"), (0,18))
    sidebar.blit(text.createTextSurf(f"{extraDataKeys[selectedExtraData]}"), (0,27))

    screen.blit(win, (sbWidth, 0))
    screen.blit(sidebar, (0,0))
    pygame.display.update()

tilemap.generateCollision({i + 1 for i in range(15)}, True)
tilemapData = tilemap.saveToJson()

for key, value in extraData.items():
    if value != []:
        tilemapData[key] = value
    if key == 'maxPumpkins':
        if len(value) >= 1:
            tilemapData[key] = int(value[0][0] / tileSize)
    if key == 'text':
        tilemapData[key] = value + [textData]

if True:
    with open(f"data/maps/level{levelNum}.json", 'w') as f:
        f.write(json.dumps(tilemapData, indent=4))

pygame.quit()