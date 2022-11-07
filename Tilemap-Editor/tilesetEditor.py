import pygame

pygame.init()

width = int(320 * 1.5)
height = int(180 * 1.5)
win = pygame.display.set_mode((width, height), pygame.SCALED | pygame.RESIZABLE, 8)
pygame.display.set_caption("Tilemap Editor")

clock = pygame.time.Clock()
fps = 60

import json, sys, os, copy
from easygui import buttonbox

from scripts.common import *
from scripts.text import Text

text = Text()
text.loadFontImg("res/text.png", scale=(1,1))

filePath = "labtiles.json" if len(sys.argv) <= 1 else sys.argv[1]

data = "{}"
if os.path.exists(filePath):
    with open(filePath, 'r') as f:
        data = f.read()
tileset = json.loads(data)
tileImgs = loadSpriteSheet(\
    tileset["imgPath"],\
    (tileset["tileSize"], tileset["tileSize"]),\
    tileset["imgTileSheetDim"],\
    tileset["imgTilePadding"], tileset["tileNum"],\
    (0,0,0)\
)

ts = TileSelection(
    (tileset["tileSize"] * 6.5, height), (35, 35, 45),\
    pygame.math.Vector2((0, 0)), tileset["tileSize"] / 2,\
    350, -1, tileImgs, tileset["tileSize"]
)
currentTile = 0
    
xOffset = ts.rect.w + 20
yOffset = 20

tileDisplaySize = tileset["tileSize"] * 4
autotileRects = []

for x, y in [(0, 1), (2, 1), (1, 0), (1, 2)]:
    #(1, 0), (2, 1), (0, 1), (1, 2)]:
    autotileRects.append(pygame.Rect((
     xOffset + x * tileDisplaySize + 1,\
     yOffset + y * tileDisplaySize + 1,\
     tileDisplaySize - 2, tileDisplaySize - 2)
    ))

buttons = {
    "collision" : pygame.Rect((xOffset + tileDisplaySize * 3 + 75, yOffset, 25, 25)),
    "enableAutotile" : pygame.Rect((xOffset + tileDisplaySize * 3 + 75, yOffset + 50, 25, 25))
}

currentSavedData = copy.deepcopy(tileset)

def saveTileset():
    global currentSavedData
    with open(filePath, 'w') as f:
        f.write(json.dumps(tileset, indent=4))
    currentSavedData = copy.deepcopy(tileset)

running = True
while running:
    clock.tick(fps)
    delta = clock.get_time() / 1000

    mousePos = pygame.math.Vector2(pygame.mouse.get_pos())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if tileset != currentSavedData:
                choice = buttonbox("", "Save changes before closing?", ("Save", "Do not save", "Cancel"), default_choice="Save", cancel_choice="Cancel")
                if choice == "Save":
                    saveTileset()
                if choice != "Cancel":
                    running = False
            else:
                running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                if pygame.key.get_mods() &pygame.KMOD_CTRL:
                    saveTileset()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, r in enumerate(ts.rects):
                rect = pygame.Rect(r)
                if rect.collidepoint(mousePos):
                    currentTile = i
            
            for i, r in enumerate(autotileRects):
                if r.collidepoint(mousePos):
                    bit = getBit(int(tileset["tiles"][currentTile]["autotile"], 2), i)
                    tileset["tiles"][currentTile]["autotile"] = bin(modifyBit(int(tileset["tiles"][currentTile]["autotile"], 2), i, not bit))
            
            for key, rect in buttons.items():
                if rect.collidepoint(mousePos):
                    tileset["tiles"][currentTile][key] = not tileset["tiles"][currentTile][key]

        if event.type == pygame.MOUSEWHEEL:
            if mousePos.x < ts.rect.w:
                scrollAmount = ts.scrollSpeed * delta * event.y * ts.scrollDir
                ts.scroll += scrollAmount
                for r in ts.rects:
                    r[1] -= scrollAmount
    
    win.fill((200,200,200))

    pygame.draw.rect(win, ts.col, ts.rect)
    win.blit(ts.surf, (ts.pos[0], ts.pos[1] - ts.scroll))
    stRect = ts.rects[currentTile % len(ts.rects)] # Selected tile rect
    pygame.draw.rect(win, (0,255,255), (stRect[0] - 1, stRect[1] - 1, stRect[2] + 1, stRect[3] + 1), width=1)

    win.blit(pygame.transform.scale(tileImgs[currentTile], (tileDisplaySize, tileDisplaySize)), (tileDisplaySize + xOffset, tileDisplaySize + yOffset))

    for i, r in enumerate(autotileRects):
        w = 0 if getBit(int(tileset["tiles"][currentTile]["autotile"], 2), i) else 1
        
        pygame.draw.rect(win, (100, 100, 125), r, width=w, border_radius=10)
        win.blit(text.createTextSurf(f"{i}"), (r.x, r.y))
    
    for key, rect in buttons.items():
        win.blit(text.createTextSurf(key), (
            rect.x - text.measureText(key)[0] - 5, rect.y + 10
        ))
        if tileset["tiles"][currentTile][key]:
            pygame.draw.rect(win, (255,255,255), rect, border_radius=5)
        pygame.draw.rect(win, (100, 100, 125), rect, width=1, border_radius=5)
    
    pygame.display.update()

pygame.quit()