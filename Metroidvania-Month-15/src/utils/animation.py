import math

class Animation:
    def __init__(self, keyFrames, speed=1, repeat="Loop", realTime=False, active=True):
        if len(keyFrames) <= 1:
            print("Not Enough Keyframes.")
            keyFrames.append(0)

        self.keyFrames = keyFrames
        self.value = self.keyFrames[0]
        self.index = 1

        self.dir = ((self.keyFrames[self.index] - self.value) > 0) * 2 - 1

        self.speed = speed

        self.realTime = realTime
        self.repeat = repeat

        self.active = active

    def start(self, restart=False):
        self.active = True
        if restart:
            self.index = 1
            self.value = self.keyFrames[0]
            self.dir = ((self.keyFrames[self.index] - self.value) > 0) * 2 - 1

    def update(self, delta):
        if self.active:
            if self.realTime:
                self.value += delta * self.speed * self.dir
            else:
                self.value += self.speed * self.dir

            if (self.dir == 1 and self.value >= self.keyFrames[self.index]) or (self.dir == 0 - 1 and self.value <= self.keyFrames[self.index]):
                self.value = self.keyFrames[self.index]
                self.index += 1

                if self.index > len(self.keyFrames) - 1:
                    if self.repeat == "Loop":
                        self.index = 1
                        self.value = self.keyFrames[0]
                    elif self.repeat == "Stop":
                        self.active = False
                        self.index = 1
                    elif self.repeat == "Stop Restart":
                        self.index = 1
                        self.value = self.keyFrames[0]
                        self.active = False

                self.dir = ((self.keyFrames[self.index] - self.value) > 0) * 2 - 1
