import pygame

class Input:
    def __init__(self):
        self.previousKeys = None
        self.currentKeys = pygame.key.get_pressed()

        self.previousMouse = None
        self.currentMouse = pygame.mouse.get_pressed()

    def update(self):
        self.previousKeys = self.currentKeys
        self.currentKeys = pygame.key.get_pressed()

        self.previousMouse = self.currentMouse
        self.currentMouse = pygame.mouse.get_pressed()

    def keyDown(self, key):
        return self.currentKeys[key]

    def keyUp(self, key):
        return not self.currentKeys[key]

    def keyJustPressed(self, key):
        return (not self.previousKeys[key] and self.currentKeys[key])

    def keyJustReleased(self, key):
        return (self.previousKeys[key] and not self.currentKeys[key])
    
    def mouseDown(self, button):
        return self.currentMouse[button]

    def mouseUp(self, button):
        return not self.currentMouse[button]

    def mouseJustPressed(self, button):
        return (not self.previousMouse[button] and self.currentMouse[button])

    def mouseJustReleased(self, button):
        return (self.previousMouse[button] and not self.currentMouse[button])