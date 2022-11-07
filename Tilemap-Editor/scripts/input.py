import pygame
import json, copy

class Input:
    def loadFromFile(self, filePath):
        data = ""
        with open(filePath, 'r') as f:
            data = f.read()
        data = json.loads(data)

        if "input" in data: data = data["input"]
        if "Input" in data: data = data["Input"]

        self.loadWithDictionary(data)

    def loadWithDictionary(self, dict):
        for action, keyNames in dict.items():
            self.currentActionMap[action] = False
            self.prevActionMap[action] = False

            for keyName in keyNames:
                key = pygame.key.key_code(keyName)

                if key in self.keyActions:
                    self.keyActions[key].append(action)
                else:
                    self.keyActions[key] = [action]
    
    def printKeyActions(self):
        for key, actions in self.keyActions.items():
            print(pygame.key.name(key), end=": [")
            for action in actions:
                print(action, end=", ")
            print("\b\b]")

    def __init__(self):
        self.keyActions = {}
        self.currentActionMap = {}
        self.prevActionMap = {}

        self.currentMouseButtons = pygame.mouse.get_pressed()
        self.prevMouseButtons = pygame.mouse.get_pressed()

    # state is True or False based on key down or up
    def eventUpdate(self, key, state):
        self.prevActionMap = copy.deepcopy(self.currentActionMap)
        if key in self.keyActions:
            for action in self.keyActions[key]:
                self.currentActionMap[action] = state
    
    def passiveUpdate(self):
        self.prevActionMap = copy.deepcopy(self.currentActionMap)

        self.prevMouseButtons = self.currentMouseButtons
        self.currentMouseButtons = pygame.mouse.get_pressed()
    
    def isActionPressed(self, action):
        return self.currentActionMap[action]
    
    def isActionReleased(self, action):
        return not self.currentActionMap[action]
    
    def isActionJustPressed(self, action):
        return self.currentActionMap[action] and not self.prevActionMap[action]
    
    def isActionJustReleased(self, action):
        return not self.currentActionMap[action] and self.prevActionMap[action]
    
    def isMouseButtonPressed(self, button):
        return self.currentMouseButtons[button]
    
    def isMouseButtonReleased(self, button):
        return not self.currentMouseButtons[button]
    
    def isMouseButtonJustPressed(self, button):
        return self.currentMouseButtons[button] and not self.prevMouseButtons[button]

    def isMouseButtonJustReleased(self, button):
        return not self.currentMouseButtons[button] and self.prevMouseButtons[button]