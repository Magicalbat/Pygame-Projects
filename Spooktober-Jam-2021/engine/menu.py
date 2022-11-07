import pygame

from engine.common import *
from engine.animation import Animation
from engine.text import Text

class Menu:
    def __init__(self, texts, fontScale, spacing, offset, functions, arguments=None, color=(255,255,255)):
        self.texts = texts
        self.spacing = spacing
        self.offset = offset
        self.functions = functions
        self.arguments = arguments

        self.selected = 0

        self.color = color

        self.imgText = Text()
        self.imgText.loadFontImg("data/images/text.png", scale=(fontScale, fontScale), color=self.color)
        self.fontScale = fontScale

        self.lineAnim = Animation([0, 1], repeat="Stop", realTime=True)
        self.changeSelected(0)

    def draw(self, win):
        for i in range(len(self.texts)):
            offset = 0
            #c = (100, 100, 100)
            if i == self.selected:
                offset = 4
                #c = (0, 0, 0)

            pos = (self.offset[0] + self.spacing[0] * i + offset,
                   self.offset[1] + self.spacing[1] * i)

            if i == self.selected:
                textSize = self.imgText.measureText(self.texts[i])
                pygame.draw.line(
                    win, self.color, (pos[0], pos[1] + textSize[1] - 2 * self.fontScale + self.fontScale),
                    (pos[0] + self.lineAnim.value, pos[1] + textSize[1] - 2 * self.fontScale + self.fontScale))

            win.blit(self.imgText.createTextSurf(self.texts[i]), pos)

    def changeSelected(self, change):
        self.selected += change
        self.selected %= len(self.texts)

        textWidth = self.imgText.measureText(self.texts[self.selected])[0]

        self.lineAnim.keyFrames[1] = textWidth
        self.lineAnim.speed = textWidth * 4
        self.lineAnim.start(True)

    def update(self, inp, delta=0):
        if inp.keyJustPressed(pygame.K_DOWN) or inp.keyJustPressed(pygame.K_RIGHT):
            self.changeSelected(1)
        if inp.keyJustPressed(pygame.K_UP) or inp.keyJustPressed(pygame.K_LEFT):
            self.changeSelected(-1)

        if inp.keyJustPressed(pygame.K_RETURN):
            if self.arguments is not None and self.selected in self.arguments:
                self.functions[self.selected](self.arguments[self.selected])
            elif self.selected in self.functions:
                self.functions[self.selected]()

        self.lineAnim.update(delta)
