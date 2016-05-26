#!/usr/bin/env python3

# Written for Python 3.4.3

import random
import math
import tkinter as tk
import tkinter.messagebox
import threading
import time
import argparse


class Hamster(object):
    '''
    position is a (x, y) tuple
    darkness is a float from 0 (white) and 1 (black)
    '''

    def __init__(self, position, darkness, neighborRadius):
        self.position = position
        self.darkness = darkness
        self.neighborRadius = neighborRadius
        self.age = 0
        self.bred = True
        self.name = self.makeName()
        self.angle = random.uniform(0, 2 * math.pi)

    def posAngNeighbors(self, neighbors):
        raise NotImplementedError

    def move(self, position):
        raise NotImplementedError

    def willDie(self):
        # Using a Weibull Distribution with l = 100, k = 15.
        # Life expectancy ~100
        l = 100
        k = 15
        t = self.age
        prob = (k / l) * ((t / l) ** (k - 1)) * math.exp(-((t / l) ** k))

        result = random.random()
        if result < prob or t > l + 10:
            print(self.name, "tragically died at the ripe old age of", self.age)
            return True
        elif result >= prob:
            return False

    def ageStep(self):
        self.age += 1

    def breed(self, neighbors):
        '''
        returns new hamster <3 if the attraction is there
        '''
        raise NotImplementedError

    def getBabyPos(self, wife):
        babyX = (self.position[0] + wife.position[0]) / 2
        babyY = (self.position[1] + wife.position[1]) / 2
        return (babyX, babyY)

    def makeName(self):
        listNames = [name.strip('\n') for name in open("names.txt", mode='r')]
        return random.choice(listNames)

    def distTo(self, hammy):
        dist = ((self.position[0] - hammy.position[0]) ** 2 +
                (self.position[1] - hammy.position[1]) ** 2) ** 0.5
        return dist


class RacistHam(Hamster):
    def posAngNeighbors(self, neighbors):
        # If no neighbors handling:
        if len(neighbors) == 0:
            return (self.position[0], self.position[1], self.angle)

        # (x, y, angle, weight difference)
        colorPos = [(hammy.position[0], hammy.position[1], hammy.angle,
                     3.0 * (1 - (abs(self.darkness - hammy.darkness))) +
                     1.5 * (self.neighborRadius - self.distTo(hammy)))
                    for hammy in neighbors]

        # Determining sum of weights
        weightSum = sum([hammy[3] for hammy in colorPos])

        # Calculate position
        posAng = (sum([hammy[0] * hammy[3] for hammy in colorPos]) / weightSum,
                  sum([hammy[1] * hammy[3] for hammy in colorPos]) / weightSum,
                  sum([hammy[2] * hammy[3] for hammy in colorPos]) / weightSum)

        return posAng

    def move(self, neighbors):
        # Find weighted position of neighbors
        posAngNeighbors = self.posAngNeighbors(neighbors)

        # Random movement
        ownBeatDist = 9
        x = random.uniform(-ownBeatDist, ownBeatDist)
        y = random.uniform(-ownBeatDist, ownBeatDist)

        # Random turning
        randTurnMax = math.radians(30)  # in degrees
        randTurn = random.uniform(-randTurnMax, randTurnMax)

        # Flock movement
        flockDist = 3
        xflock = flockDist * math.cos(self.angle)
        yflock = flockDist * math.sin(self.angle)

        # Weights for updating angles, positions
        ownBeatWeight = 1.40
        followerWeight = 0.60
        weightTot = ownBeatWeight + followerWeight

        # Updating position
        self.position = ((ownBeatWeight * self.position[0] +
                          followerWeight * posAngNeighbors[0]) / weightTot +
                         x + xflock,
                         (ownBeatWeight * self.position[1] +
                          followerWeight * posAngNeighbors[1]) / weightTot +
                         y + yflock)

        # Updating angle
        self.angle = (ownBeatWeight * self.angle +
                      followerWeight * posAngNeighbors[2]) / weightTot + \
            randTurn

    def breed(self, neighbors):
        '''
        Racist hamster prefers his own color.  The probability of mating with
        any one hamster is a linear combination of weighted standard deviations
        for age and color
        '''
        random.shuffle(neighbors)
        for hammy in neighbors:
            ageTest = abs(self.age - hammy.age) <= 30
            colorTest = abs(self.darkness - hammy.darkness) <= 0.4

            # Breed!
            if random.random() < 0.45 and ageTest and colorTest \
               and len(neighbors) < 10 and not self.bred:
                babyPos = self.getBabyPos(hammy)
                darkness = (self.darkness + hammy.darkness) / 2
                neighborRadius = self.neighborRadius
                self.bred = True
                baby = RacistHam(babyPos, darkness, neighborRadius)
                print(self.name, "and", hammy.name, "gave birth to the",
                      "beautiful baby", baby.name)
                return baby

        return False


class Field(object):
    '''
    self.hamsters is a list of hamster objects
    self.size is a tuple describing the size of the playground
    '''

    def __init__(self, hamsters, size, doGraphics):
        self.size = size
        self.hamsters = hamsters
        self.doGraphics = doGraphics

    def getNeighbors(self, hamster):
        neighbors = []
        for hammy in self.hamsters:
            dist = ((hamster.position[0] - hammy.position[0]) ** 2 +
                    (hamster.position[1] - hammy.position[1]) ** 2) ** 0.5
            if dist <= hamster.neighborRadius and hammy != hamster:
                neighbors.append(hammy)
        return neighbors

    def showHamsters(self):
        # Clear Window
        theCanvas.delete('all')

        # Do Hamsters
        for hamster in self.hamsters:
            # Representation Characteristics
            color = hex(int(hamster.darkness * 255))
            colorstring = '#' + 3*color.split('x')[-1]
            outlinecolor = 'red' if hamster.age <= 5 else 'black'
            outlinewidth = 2 if hamster.age <= 5 else 1
            scale = 6 + hamster.age // 20

            hamster.rep = theCanvas.create_oval(int(hamster.position[0]),
                                                int(hamster.position[1]),
                                                int(hamster.position[0] +
                                                    scale),
                                                int(hamster.position[1] +
                                                    scale),
                                                fill=colorstring,
                                                outline=outlinecolor,
                                                width=outlinewidth)

        theWindow.update()

    def updateField(self, i):
        # Kill the Oldies
        self.hamsters = [hammy for hammy in self.hamsters
                         if not hammy.willDie()]

        for hammy in self.hamsters:
            neighbors = self.getNeighbors(hammy)

            # Breed them <3
            baby = hammy.breed(neighbors)
            if baby is not False:
                self.hamsters.append(baby)

            # Move them
            hammy.move(neighbors)

            # Check not out of bounds
            if hammy.position[0] > self.size[0]:
                hammy.position = (self.size[0], hammy.position[1])
                hammy.angle = math.radians(180)  # in degrees
            elif hammy.position[0] < 0:
                hammy.position = (0, hammy.position[1])
                hammy.angle = math.radians(0)  # in degrees
            if hammy.position[1] > self.size[1]:
                hammy.position = (hammy.position[0], self.size[1])
                hammy.angle = math.radians(-90)  # in degrees
            elif hammy.position[1] < 0:
                hammy.position = (hammy.position[0], 0)
                hammy.angle = math.radians(90)  # in degrees

            # Age them
            hammy.ageStep()

            # Make them breedable again
            hammy.bred = False

        # Show Hamsters
        if self.doGraphics:
            self.showHamsters()

        # Print Status
        print()
        print("Good work fam!  We completed round", i + 1)
        print("There are currently", len(self.hamsters), "hamsters abound")
        print()
        print()


def getInitialHamsters(number, size, neighborRadius, HamClass):
    hamsters = []
    while len(hamsters) < number:
        pos = (random.uniform(0, size[0]), random.uniform(0, size[1]))
        darkness = random.random()
        hamsters.append(HamClass(pos, darkness, neighborRadius))

    return hamsters


def isYes(input):
    input = input.lower()
    if input in ['y', 'yes', 'ye', 'es']:
        return True
    elif input in ['n', 'no', 'o']:
        return False
    else:
        return None


def isNo(input):
    if isYes(input):
        return False
    elif isYes(input) == False:
        return True
    elif isYes(input) == None:
        return None


def welcome():
    print()
    print("Welcome to the Hamster simulator!")
    print()
    with open('ham_art.txt') as ham:
        for line in ham:
            print(line.strip('\n'))
    print()


def makeSettings():
    # Get input settings
    parser = argparse.ArgumentParser(prog='simulator')
    parser.add_argument('-t', '--trials', default=500, type=int, dest='trials',
                        help='Number of trials to perform')
    parser.add_argument('-w', '--width', default=600, type=int, dest='width',
                        help='Width of the window')
    parser.add_argument('-v', '--vertical', default=500, type=int,
                        dest='height', help='Height of the window')
    parser.add_argument('-n', '--number', default=40, type=int,
                        dest='initNumHamsters', help='Number of hamsters to \
                        begin with')
    parser.add_argument('-r', '--radius', default=30, type=int,
                        dest='neighborRadius', help='Radius for hamsters to \
                        consider as neighbors')

    return vars(parser.parse_args())


def runSimulation(trials):
    for i in range(trials):
        theField.updateField(i)
        if len(theField.hamsters) == 0:
            break
        # To slow down simulation
        if doGraphics:
            time.sleep(1/60)

    print()
    print('Simulation completed!')
    print('After',  i + 1,
          'trials, there were', len(theField.hamsters), 'alive.')
    print()
    print('Goodbye!')
    if doGraphics:
        if tkinter.messagebox.showinfo(title='Quit?',
                                       message='The simulation has ended'):
            theWindow.destroy()


def main():
    # Parse Command-line
    settings = makeSettings()

    # Welcome
    welcome()

    # Do Graphics?
    resp = input('Would you like a graphical simulation? (y/n): ')
    global doGraphics
    doGraphics = True if isYes(resp) else False

    # Initialize Objects
    initHamsters = getInitialHamsters(settings['initNumHamsters'],
                                      (settings['width'], settings['height']),
                                      settings['neighborRadius'],
                                      RacistHam)
    global theField
    theField = Field(initHamsters, (settings['width'], settings['height']),
                     doGraphics)

    # Initialize Graphics
    if doGraphics:
        try:
            global theWindow
            theWindow = tk.Tk()
            geom = str(settings['width']) + 'x' + str(settings['height'])
            theWindow.geometry(geom)
            theWindow.title('Simulation')
            global theCanvas
            theCanvas = tk.Canvas(theWindow, width=settings['width'],
                                  height=settings['height'])
            theCanvas.pack()

        except:
            print('There was an error with the graphics module.  Confirm \
                    that you have X, Tk, and Tkinter installed.')
            raise

    else:
        print('No graphics')

    # Run Loop
    simThread = threading.Thread(target=runSimulation(settings['trials']))
    simThread.start()

    if doGraphics:
        theWindow.mainloop()


if __name__ == "__main__":
    main()
