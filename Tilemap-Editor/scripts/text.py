import pygame

from scripts.common import *

class Text():
    def __init__(self):
        self.fontImg = None
        self.chars = {} #Char: [width, img]
        self.maxCharDim = []
        self.scale = 1

        self.defaultWidths = {'A':3, 'B':3, 'C':3, 'D':3, 'E':3, 'F':3, 'G':3, 'H':3, 'I':3, 'J':3, 'K':3, 'L':3, 'M':5, 'N':3, 'O':3, 'P':3, 'Q':3, 'R':3, 'S':3, 'T':3, 'U':3, 'V':3, 'W':5, 'X':3, 'Y':3, 'Z':3, 'a':3, 'b':3, 'c':3, 'd':3, 'e':3, 'f':3, 'g':3, 'h':3, 'i':2, 'j':3, 'k':3, 'l':2, 'm':5, 'n':3, 'o':3, 'p':3, 'q':3, 'r':3, 's':3, 't':3, 'u':3, 'v':3, 'w':5, 'x':3, 'y':3, 'z':3, '.':2, '-':3, ',':3, ':':2, '+':4, "'":2, '!':2, '?':3, '0':3, '1':3, '2':3, '3':3, '4':3, '5':3, '6':3, '7':3, '8':3, '9':3, '(':2, ')':2, '/':3, '_':5, '=':3, '\\':3, '[':2, ']':2, '*':3, '"':3, '<':3, '>':3, ';':2}
    
    def loadFontImg(self, imgPath, maxDim=(5,8), charWidths=None, padding=1, color=(255,255,255), colorKey=(0,0,0), scale=(1,1)):
        self.fontImg = pygame.image.load(imgPath).convert()
        self.fontImg.set_colorkey(colorKey)
        
        if color != (255,255,255):
            self.fontImg = swapImgColor(self.fontImg, (255, 255, 255), color)

        self.maxCharDim = maxDim

        self.scale = scale

        self.chars = {}

        if charWidths is None:
            charWidths = self.defaultWidths

        for i, d in enumerate(charWidths.items()):
            key, item = d
            
            charRect = (i * (maxDim[0] + padding), 0, item, maxDim[1])

            self.chars[key] = (item, pygame.transform.scale(self.fontImg.subsurface(charRect).convert(), (self.scale[0] * charRect[2], self.scale[1] * charRect[3])))
    
    def measureText(self, msg):
        return (sum(((self.chars[c][0] + 1) * self.scale[0] if c != ' ' and c != '\n' else self.maxCharDim[0] * self.scale[0] for c in msg)), self.maxCharDim[1] * self.scale[1] + sum((self.maxCharDim[1] * self.scale[1] for c in msg if c == '\n')))
    
    def createTextSurf(self, msg):
        surf = pygame.Surface(self.measureText(msg)).convert()
        surf.set_colorkey((0,0,0))

        offset = pygame.math.Vector2(0,0)
        for c in msg:
            if c in self.chars:
                surf.blit(self.chars[c][1], offset)

                offset.x += (self.chars[c][0] + 1) * self.scale[0]
            elif c == ' ':
                offset.x += (self.maxCharDim[0]) * self.scale[0]
            elif c == '\n':
                offset.x = 0
                offset.y += self.maxCharDim[1] * self.scale[1]
        
        return surf
