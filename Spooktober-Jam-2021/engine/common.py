import pygame

def lerp(a, b, f):
    return a + f * (b - a)

# Value, Lower Bounds, Upper Bounds
def clamp(a, l, u):
    return min(u, max(a, l))

def getCollidingRects(testRect, rects):
    hitlist = []

    for rect in rects:
        if testRect.colliderect(rect):
            hitlist.append(rect)

    return hitlist

def optimizeTilemapCollision(rects, tileSize):
    outRects = []
    usedRects = []

    for rect in rects:
        if rect in usedRects:
            continue

        width = tileSize
        offset = 1
        goingRight = True

        while goingRight:
            testRect = pygame.Rect(
                (rect.x + offset * tileSize, rect.y, tileSize, tileSize))

            if testRect in rects and testRect not in usedRects:
                width += tileSize
                offset += 1

                usedRects.append(testRect)
            else:
                goingRight = False

        height = tileSize
        offset = 1
        goingDown = True

        while goingDown:
            testRects = [pygame.Rect((rect.x + i * tileSize, rect.y + offset * tileSize, tileSize, tileSize)) for i in range(int(width / tileSize))]

            for tr in testRects:
                if tr not in rects or tr in usedRects:
                    goingDown = False
                    break

            if not goingDown:
                break

            height += tileSize
            offset += 1

            for tr in testRects:
                usedRects.append(tr)

        outRects.append(pygame.Rect(rect.x, rect.y, width, height))

    return outRects

def loadSpriteSheet(imgPath, spriteSize, dim, padding, count, colorKey=None):
    mainImg = pygame.image.load(imgPath).convert()

    if colorKey is not None:
        mainImg.set_colorkey(colorKey, pygame.RLEACCEL)
    
    imgs = []

    i = 0
    for y in range(dim[1]):
        for x in range(dim[0]):
            rect = pygame.Rect(x * (spriteSize[0] + padding[0]), y * (spriteSize[0] + padding[1]), spriteSize[0], spriteSize[1])
            
            rect.right = min(rect.right, mainImg.get_width())
            rect.bottom = min(rect.bottom, mainImg.get_height())

            imgs.append(mainImg.subsurface(rect))

            i += 1

            if i > count - 1:
                return imgs
    
    return imgs

# Adapted from https://www.pygame.org/wiki/Spritesheet
def loadSpriteSheetOld(imgPath, spriteSize, dim, padding, count, colorKey=None):
    mainImg = pygame.image.load(imgPath).convert()

    imgs = []

    i = 0
    for y in range(dim[1]):
        for x in range(dim[0]):
            rect = pygame.Rect(x * (spriteSize[0] + padding[0]), y * (spriteSize[0] + padding[1]), spriteSize[0], spriteSize[1])

            img = pygame.Surface(rect.size).convert()
            img.blit(mainImg, (0, 0), rect)

            if colorKey is not None:
                if colorKey == -1:
                    colorKey = img.get_at((0, 0))
                img.set_colorkey(colorKey, pygame.RLEACCEL)

            imgs.append(img)

            i += 1

            if i > count - 1:
                return imgs

    return imgs

def setCursorFromTxt(filePath):
    lines = None
    with open(filePath, 'r') as f:
        lines = f.read().split('\n')
    
    hotspot = [0,0]

    if ';' in lines[0]:
        pStr = lines[0].split(';')
        hotspot = [int(pStr[0]), int(pStr[1])]
        lines.pop(0)

    xormasks, andmasks = pygame.cursors.compile(lines)
    pygame.mouse.set_cursor((len(lines), len(lines[0])), hotspot, xormasks, andmasks)

def setCursorFromImg(imgPath, hotspotChar="X", txtFilePath=""):
    img = pygame.image.load(imgPath).convert_alpha()

    hotspot = []
    lines = []
    for y in range(img.get_height()):
        line = ""
        for x in range(img.get_width()):
            if img.get_at((x, y)) == (0,0,0):
                line += "X"
            elif img.get_at((x, y)) == (255,255,255):
                line += "."
            elif img.get_at((x, y)) == (255,0,0):
                hotspot = [x, y]
                line += hotspotChar
            else:
                line += " "
        lines.append(line)

    if txtFilePath != "":
        with open(txtFilePath, 'w') as f:
            f.write(f"{hotspot[0]};{hotspot[1]}\n")
            for i in range(len(lines)):
                if i == len(lines) - 1:
                    f.write(lines[i])
                else:
                    f.write(lines[i] + '\n')

    
    xormasks, andmasks = pygame.cursors.compile(lines)
    pygame.mouse.set_cursor((len(lines), len(lines[0])), hotspot, xormasks, andmasks)

#Takes a dictionary
def floodFill(map, pos, newVal, prevVal=None, initPos=None):
    if initPos == None:
        initPos = pos

    if abs(pos[0] - initPos[0]) > 15 or abs(pos[1] - initPos[1]) > 15:
        return

    pos = tuple(pos)
    
    if pos not in map:
        if prevVal != None:
            return
    else:
        if map[pos] != prevVal:
            return
        if map[pos] == newVal:
            return

    map[pos] = newVal

    floodFill(map, (pos[0] + 1, pos[1]), newVal, prevVal, initPos)
    floodFill(map, (pos[0] - 1, pos[1]), newVal, prevVal, initPos)
    floodFill(map, (pos[0], pos[1] + 1), newVal, prevVal, initPos)
    floodFill(map, (pos[0], pos[1] - 1), newVal, prevVal, initPos)

def swapImgColor(img, oldCol, newCol):
    outImg = pygame.Surface((img.get_width(), img.get_height()))
    outImg.fill(newCol)

    imgCopy = img.copy()
    imgCopy.set_colorkey(oldCol)

    outImg.blit(imgCopy, (0,0))

    outImg.set_colorkey(img.get_colorkey())
    
    return outImg