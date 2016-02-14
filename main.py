# Written for Python 3.4.3

import random
import math
import tkinter as tk
import tkinter.messagebox
import threading


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
        self.name = self.getName()

    def posNeighbors(self, neighbors):
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
        if result < prob or t > 110:
            print(self.name, "died at the ripe old age of", self.age)
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

    def getName(self):
        listNames = [name.strip('\n') for name in open("names.txt", mode='r')]
        return random.choice(listNames)


class RacistHam(Hamster):
    def posNeighbors(self, neighbors):
        # If no neighbors handling:
        if len(neighbors) == 0:
            return self.position

        # (position, 1/weight)
        colorposX = [(hammy.position[0], (self.darkness - hammy.darkness))
                     for hammy in neighbors]
        colorposY = [(hammy.position[1], (self.darkness - hammy.darkness))
                     for hammy in neighbors]

        # Determining sum of weights
        weightSum = 0
        for hammy in colorposX:
            invWeight = max(hammy[1], 0.01)
            weightSum += 1 / invWeight

        # Calculating X
        Xpos = 0
        for hammy in colorposX:
            Xpos += hammy[0] * hammy[1]
        Xpos = Xpos / weightSum

        # Calculating Y
        Ypos = 0
        for hammy in colorposY:
            Ypos += hammy[0] * hammy[1]
        Ypos = Ypos / weightSum

        return (Xpos, Ypos)

    def move(self, neighbors):
        # Find weighted position of neighbors
        posNeighbors = self.posNeighbors(neighbors)

        # Random degree
        x = random.uniform(-10, 10)
        y = random.uniform(-10, 10)

        self.position = ((1.25 * self.position[0] + 0.75 * posNeighbors[0]) /
                         2 + x,
                         (1.25 * self.position[1] + 0.75 * posNeighbors[1]) /
                         2 + y)

    def breed(self, neighbors):
        '''
        Racist hamster prefers his own color.  The probability of mating with
        any one hamster is a linear combination of weighted standard deviations
        for age and color
        '''
        random.shuffle(neighbors)
        for hammy in neighbors:
            avgDarkness = (self.darkness + hammy.darkness) / 2
            avgAge = max([(self.age + hammy.age)/2, 1])
            prob = 1 - (((self.darkness - hammy.darkness) ** 2) / avgDarkness) \
                - (((self.age - hammy.age) ** 2) / avgAge)

            # Breed!
            if random.random() < prob and len(neighbors) < 10 and not self.bred:
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
            color = hex(int(hamster.darkness * 255))
            colorstring = '#' + 3*color.split('x')[-1]
            hamster.rep = theCanvas.create_oval(int(hamster.position[0]),
                                                int(hamster.position[1]),
                                                int(hamster.position[0] + 6),
                                                int(hamster.position[1] + 6),
                                                fill=colorstring)

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
            elif hammy.position[0] < 0:
                hammy.position = (0, hammy.position[1])
            if hammy.position[1] > self.size[1]:
                hammy.position = (hammy.position[0], self.size[1])
            elif hammy.position[1] < 0:
                hammy.position = (hammy.position[0], 0)

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


def getInitialHamsters(number, size, HamClass):
    hamsters = []
    while len(hamsters) < number:
        pos = (random.uniform(0, size[0]), random.uniform(0, size[1]))
        darkness = random.random()
        neighborRadius = 40
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


def runSimulation(trials):
    for i in range(trials):
        theField.updateField(i)
        if len(theField.hamsters) == 0:
            break
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
    # Welcome
    welcome()
    resp = input('Would you like a graphical simulation? (y/n): ')
    global doGraphics
    doGraphics = True if isYes(resp) else False

    # Values
    trials = 1000
    size = (600, 500)
    numHamsters = 40
    initHamsters = getInitialHamsters(numHamsters, size, RacistHam)
    global theField
    theField = Field(initHamsters, size, doGraphics)

    # Initialize Graphics
    if doGraphics:
        try:
            global theWindow
            theWindow = tk.Tk()
            geom = str(size[0]) + 'x' + str(size[1])
            theWindow.geometry(geom)
            theWindow.title('Simulation')
            global theCanvas
            theCanvas = tk.Canvas(theWindow, width=size[0], height=size[1])
            theCanvas.pack()

        except:
            print('There was an error with the graphics module.  Confirm \
                    that you have X, Tk, and Tkinter installed.')
            raise

    else:
        print('No graphics')

    # Run Loop
    simThread = threading.Thread(target=runSimulation(trials))
    simThread.start()

    if doGraphics:
        theWindow.mainloop()


if __name__ == "__main__":
    main()
