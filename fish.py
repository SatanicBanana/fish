import time
import os
import random
import shutil
import sys
import msvcrt

simSpeed = 40

# the fish. it animates.

#     >[###]>
#      >[###]
#       >[###
#        >[##
#         >[#
#          >[
#           >
#           <
#          <[
#         <[#
#        <[##
#       <[###
#      <[###]
#     <[###]<

# controls IDs for fish (prevents weird drawing artifacts)
class IDController:
    def __init__(self):
        self.idFsh = 0

    def Assign(self):
        self.idFsh += 1
        return self.idFsh - 1

    def Release(self):
        self.idFsh -= 1

class FishChild:
    def __init__(self, parent, sprite, value):
        self.id = idc.Assign()
        self.p = False
        self.parent = parent
        self.sprite = sprite
        self.spriteLength = len(sprite)
        self.value = value
        self.parent.children.append(self)

        if parent.rev == -1:
            self.sprite = ReverseFish(self.sprite)

        self.up()

    def up(self):
        self.yPos = self.parent.yPos + self.value
        self.xPos = self.parent.xPos
        self.rev = self.parent.rev
        self.movCounter = self.parent.movCounter
        self.turningState = self.parent.turningState  # -1 - not turning, 0 - turning start, 1 - turning end
        self.turnCount = self.parent.turnCount

class Fish:
    def __init__(self, y, data):
        self.id = idc.Assign()
        self.p = False
        self.yPos = y
        self.data = data
        self.sprite = data.sprite
        self.spriteLength = len(data.sprite)
        self.rev = random.choice([-1, 1])
        self.xPos = (0 - self.spriteLength) if self.rev == 1 else (oceanLength + self.spriteLength)
        self.speed = random.choice(data.speeds) * self.rev
        self.children = []
        if self.rev == -1:
            self.sprite = ReverseFish(self.sprite)

        self.movCounter = 0

        self.turningState = -1 # -1 - not turning, 0 - turning start, 1 - turning end
        self.turnCount = 0

    def up(self):
        # if we are currently turning, ignore all of this shit
        if self.turningState != -1:
            # basically, we chop off parts of the sprite until we hit the length of the sprite - 1, then switch sprite and take those chops off.
            # In the context of the update, we increment turnCount to the limit, change turnState, reverse the sprite and speed, reduce it back to 0 and set turnState to -1 again.
            # This is reversed if the fish is going the other way.
            if self.turningState == 0:
                self.turnCount += int(self.spriteLength // 4)
                self.xPos += 2 if self.rev == 1 else -1
                if self.turnCount >= self.spriteLength:
                    self.turningState = 1
                    self.turnCount = self.spriteLength - 1
                    self.xPos -= 1 if self.rev == 1 else -1
                    self.speed *= -1
                    self.rev *= -1
                    for child in self.children:
                        child.sprite = ReverseFish(child.sprite)

                    self.sprite = ReverseFish(self.sprite)

            if self.turningState == 1:
                self.turnCount -= int(self.spriteLength // 4)
                self.xPos -= 1 if self.rev == -2 else 0
                if self.turnCount <= 0:
                    self.turningState = -1
                    self.turnCount = 0

        else:
            if random.randint(0, int(120 / abs(self.speed))) == 5:
                self.turningState = 0

            self.movCounter += self.speed
            while self.movCounter >= 1:
                self.xPos += 1
                self.movCounter -= 1

            while self.movCounter <= -1:
                self.xPos -= 1
                self.movCounter += 1

            # move y position
            # it'll become less likely for the fish to move in a direction as it approaches the boundary of the direction

            #up
            chance = self.data.yUp + ((50 - self.yPos) / 5)
            if random.randint(0, 50) > chance:
                self.yPos -= 1

            chance = self.data.yDown + (self.yPos / 5)
            if random.randint(0, 50) > chance:
                self.yPos += 1

            self.yPos = max(0, min(self.yPos, oceanDepth - 1))

            if (self.xPos >= oceanLength + self.spriteLength and self.rev == 1) or (self.xPos <= -self.spriteLength and self.rev == -1):
                return True
            else:
                return False

# a copy of the fish class but with the up() function cannibalised so that the player can control it instead
class PlayerFish:
    def __init__(self, y, data):
        self.id = idc.Assign()
        self.p = True
        self.yPos = y
        self.data = data
        self.sprite = data.sprite
        self.spriteLength = len(data.sprite)
        self.rev = 1
        self.xPos = (0 - self.spriteLength) if self.rev == 1 else (oceanLength + self.spriteLength)
        self.speed = random.choice(data.speeds) * self.rev
        self.vspeed = 0
        self.vcounter = 0
        self.children = []
        if self.rev == -1:
            self.sprite = ReverseFish(self.sprite)

        self.movCounter = 0

        self.turningState = -1 # -1 - not turning, 0 - turning start, 1 - turning end
        self.turnCount = 0

    # doesn't turn automaticslly
    # doesn't change y automatically
    # is not destroyed
    def up(self):
        # if we are currently turning, ignore all of this shit
        if self.turningState != -1:
            # basically, we chop off parts of the sprite until we hit the length of the sprite - 1, then switch sprite and take those chops off.
            # In the context of the update, we increment turnCount to the limit, change turnState, reverse the sprite and speed, reduce it back to 0 and set turnState to -1 again.
            # This is reversed if the fish is going the other way.
            if self.turningState == 0:
                self.turnCount += int(self.spriteLength // 4)
                self.xPos += 2 if self.rev == 1 else -1
                if self.turnCount >= self.spriteLength:
                    self.turningState = 1
                    self.turnCount = self.spriteLength - 1
                    self.xPos -= 1 if self.rev == 1 else -2
                    self.speed *= -1
                    self.rev *= -1
                    for child in self.children:
                        child.sprite = ReverseFish(child.sprite)

                    self.sprite = ReverseFish(self.sprite)

            if self.turningState == 1:
                self.turnCount -= int(self.spriteLength // 4)
                self.xPos -= 2 if self.rev == -1 else -1
                if self.turnCount <= 0:
                    self.turningState = -1
                    self.turnCount = 0

        else:
            #if random.randint(0, int(120 / abs(self.speed))) == 5:
            #    self.turningState = 0

            self.movCounter += self.speed
            while self.movCounter >= 1:
                self.xPos += 1
                self.movCounter -= 1

            while self.movCounter <= -1:
                self.xPos -= 1
                self.movCounter += 1

            self.vcounter += self.vspeed
            while self.vcounter >= 1:
                self.yPos += 1
                self.vcounter -= 1

            while self.vcounter <= 1:
                self.yPos -= 1
                self.vcounter += 1

            # move y position
            # it'll become less likely for the fish to move in a direction as it approaches the boundary of the direction

            ##up
            #chance = self.data.yUp + ((50 - self.yPos) / 5)
            #if random.randint(0, 50) > chance:
            #    self.yPos -= 1

            #chance = self.data.yDown + (self.yPos / 5)
            #if random.randint(0, 50) > chance:
            #    self.yPos += 1

            self.yPos = max(0, min(self.yPos, oceanDepth - 1))
    
            # if the fish goes offscreen, launch that fucker back in
            if (self.xPos >= oceanLength + (self.spriteLength) / 2 and self.rev == 1):
                self.speed -= 7
            if (self.xPos <= -(self.spriteLength) / 2 and self.rev == -1):
                self.speed += 7
            
            return False

class FishData:
    def __init__(self, sprite, speeds, yDown, yUp):
        self.sprite = sprite
        self.speeds = speeds
        self.yDown = yDown
        self.yUp = yUp

def ReverseFish(revFish):
    start = [">", "<", "]", "[", "}", "{", "/", "\\"]
    code =  ["1", "2", "3", "4", "5", "6", "7", "8" ]
    end =   ["<", ">", "[", "]", "{", "}", "\\", "/"]

    for i in range(0, len(start)):
        revFish = revFish.replace(start[i], code[i])

    for i in range(0, len(end)):
        revFish = revFish.replace(code[i], end[i])

    return revFish[::-1]

def LoadFishFromFile(path, multiline=False):
    file = open(path, "r")
    fArr = []
    if multiline:
        
        print("nop")
    else:
        # ><>|1/1.25/1.5|40/40
        # becomes
        # FishData("><>", [1, 1.25, 1.5], 40, 40)
        for line in file:
            lineData = line.split("|")
            #sprite needs nothing
            #speeds need to become an array of floats
            lineData[1] = lineData[1].split("/")
            for i in range(0, len(lineData[1])):
                lineData[1][i] = float(lineData[1][i])
            
            # up and down need to be ints but we can cast them in the definition can't we
            fArr.append(FishData(lineData[0], lineData[1], int(lineData[2]), int(lineData[3])))
        
        return fArr
        

def GenerateMultilineFish(fishes, fish, player=False):
    if player:
        fParent = PlayerFish(random.randint(0, oceanDepth), fish[0])
    else:
        fParent = Fish(random.randint(0, oceanDepth), fish[0])
    fChildren = []

    for i in range(1, len(fish)):
        fChildren.append(FishChild(fParent, fish[i], i))

    fishes.append(fParent)
    for f in fChildren:
        fishes.append(f)

    return fParent

def GenFloor(variance, timeout):
    # generates an array (with length of ocean floor) with heights of ground
    floor = []
    level = 4
    ti = 0
    for i in range(0, oceanLength):
        ti += 1
        if ti >= timeout and random.randint(0, 100) <= variance:
            ti = 0
            level += random.choice([-1, 1])

        level = max(0, min(level, 8))
        floor.append(level + (oceanDepth - (skyHeight * 2)) - 4)

    return floor

def cls():
    os.system('cls')

def GetFishesOnY(fishes, y):
    f = []
    for fish in fishes:
        if fish.yPos == y:
            f.append(fish)

    return f

# set the shit to the shit

input("\n\n\n\n\n                   WASD TO CONTROL PLAYER FISH\n\n                   HIT F11 (FULLSCREEN) FOR GOOD RESULTS\n\n               CONITNUE WITH ENTER>>>>")

try:
    dimensions = shutil.get_terminal_size()
    oceanDepth = shutil.get_terminal_size()[1] - 15
    skyHeight = int(oceanDepth // 10)
    oceanLength = shutil.get_terminal_size()[0] - 10
except:
    input("we fucked up help\n\nexception info below\n\n{}".format(sys.exc_info()))
    exit()

def DrawOcean(fishes, floor):
    txt = "\n" * skyHeight + "\n"
    for y in range(0, oceanDepth):
        line = ""
        f = GetFishesOnY(fishes, y)
        #fishCount = -1
        #curFish = None
        fishDraw = []
        lastFloor = floor[0]
        for x in range(-20, oceanLength):
            charAdding = ""
            madeMark = False

            # check for fish
            for fish in f:
                if fish.xPos == x:
                    fishDraw.append([fish, -1])

            #draw fish
            highestID = 999999
            for d in fishDraw:
                d[1] += 1
                if d[1] > -1:
                    if d[1] < (d[0].spriteLength - d[0].turnCount):
                        if d[0].id < highestID:  # lowest id is drawn
                            charAdding = d[0].sprite[d[1] if d[0].rev == 1 else d[1] + d[0].turnCount]
                            highestID = d[0].id
                            madeMark = True
                    else:
                        fishDraw.remove(d)

            if not madeMark:
                if y == 0:
                    charAdding = "-"
                else:
                    charAdding = " "

            # overwrite with floor if needed
            # if floor is different from last, use / (greater) or \ (lesser)
            if y >= floor[x]:
                if y == floor[x]:
                    if floor[x] > lastFloor:
                        charAdding = "\\"
                    elif floor[x] == y:
                        charAdding = "_"

                    # if the next floor is greater
                    try:
                        if floor[x + 1] < floor[x]:
                            charAdding = "/"
                    except:
                        charAdding = "_"
                else:
                    charAdding = " "

            lastFloor = floor[x]

            if x <= 10:
                charAdding = " "

            if x >= 0:
                line += charAdding
        txt += line + "\n"

    cls()
    print(txt)

f = []
timeout = 0

fDat = LoadFishFromFile("fish.txt", multiline=False)
#fDat =[FishData("><>", [1], 20, 20)]

#     ________
# \  /        \
#  >|          >
# /  \________/

fDatMultiline = [
    [FishData("    ________  ", [0.5, 0.7, 0.8], 48, 48),
              "\  /        \ ",
              " >|          >",
              "/  \________/ "],
    [FishData("___         ________|\______    ", [0.2, 0.3, 0.4], 49, 49),
              "\  \       |                \   ",
              " \  \      |             O   \  ",
              "  \  \____/                ___\ ",
              "   \                      |     ",
              "   /  ____                |____ ",
              "  /  /    \                   / ",
              " /  /      |                 /  ",
              "/__/       |______\_\_\_\___/   "]
]

idc = IDController()

floor = GenFloor(25, 5)

timeValues = [20, 200]
timers = [1, 1]

playerFish = GenerateMultilineFish(f, fDatMultiline[0], player=True)
playerFish.speed = 15
playerFish.yPos = 10

#playerFish = PlayerFish(20, FishData(">|||>", [10], 50, 50))
#f.append(playerFish)

#try:
while True:
    if dimensions != shutil.get_terminal_size():
        dimensions = shutil.get_terminal_size()
        oceanDepth = dimensions[1] - 15
        skyHeight = int(oceanDepth // 10)
        oceanLength = dimensions[0] - 10
        floor = GenFloor(25, 5)

    # do player things
    playerFish.speed *= 0.9
    playerFish.vspeed *= 0.9

    if msvcrt.kbhit():
        key = ord(msvcrt.getch())
        if chr(key) == "w":
            playerFish.vspeed -= 0.2 * abs(playerFish.speed)
        elif chr(key) == "s":
            playerFish.vspeed += 0.2 * abs(playerFish.speed)

        elif chr(key) == "a":
            if playerFish.rev == 1 and playerFish.turningState == -1:
                playerFish.turningState = 0
            playerFish.speed -= 1

        elif chr(key) == "d":
            if playerFish.rev == -1 and playerFish.turningState == -1:
                playerFish.turningState = 0
            playerFish.speed += 1

    time.sleep(1 / simSpeed)
    for i in range(0, len(timers)):
        timers[i] -= 1

    if timers[0] <= 0:
        # create a fish
        fChoice = random.choice(fDat)

        f.append(Fish(random.randint(0, oceanDepth), fChoice))
        timers[0] = random.randint(int(timeValues[0] / 4), timeValues[0])

    if timers[1] <= 0:
        # create a big fish
        fChoice = random.choice(fDatMultiline)

        GenerateMultilineFish(f, fChoice)
        timers[1] = random.randint(int(timeValues[1] / 4), timeValues[1])

    for fish in f:
        if fish.up():
            for fc in fish.children:
                idc.Release()
                f.remove(fc)

            idc.Release()
            f.remove(fish)

    # draw the ocean LAST because i'm not retarded
    DrawOcean(f, floor)
#except:
#    input("we fucked up help\n\nexception info below\n\n{}".format(sys.exc_info()))