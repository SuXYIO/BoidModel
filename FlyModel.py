from matplotlib import pyplot as plt
from math import sqrt
from random import random, sample

SWARMSIZE = 128
MOVEFRAC = 0.5
CLOSEDIST = 0.4
RANDWILL = 2

XLIM = [0, 32]
YLIM = [0, 32]
TICKRATE = 0.1

swarmX = []
swarmY = []

def euclidDist(x0, y0, x1, y1):
    return sqrt((x0 - x1)**2 + (y0 - y1)**2)

def updateFly(ind):
    x = swarmX[ind]
    y = swarmY[ind]
    d = []
    dind = []

    # Find nearest fish
    for i in range(SWARMSIZE):
        if i == ind:
            continue
        d.append(euclidDist(x, y, swarmX[i], swarmY[i]))
        dind.append(i)
    td = min(d)
    tind = dind[d.index(td)]
    tx = swarmX[tind]
    ty = swarmY[tind]

    #Move
    if td > CLOSEDIST:
        # Head to nearest fish
        swarmX[ind] += MOVEFRAC * (tx - x)
        swarmY[ind] += MOVEFRAC * (ty - y)
    else:
        # Move towards opposite direction
        swarmX[ind] -= MOVEFRAC * (tx - x)
        swarmY[ind] -= MOVEFRAC * (ty - y)
    swarmX[ind] += random() * RANDWILL * sample([1, -1], k = 1)[0]
    swarmY[ind] += random() * RANDWILL * sample([1, -1], k = 1)[0]
    if swarmX[ind] < XLIM[0]:
        swarmX[ind] = XLIM[0]
    elif swarmX[ind] > XLIM[1]:
        swarmX[ind] = XLIM[1]
    if swarmY[ind] < YLIM[0]:
        swarmY[ind] = YLIM[0]
    elif swarmY[ind] > YLIM[1]:
        swarmY[ind] = YLIM[1]

def updateSwarm():
    for i in range(SWARMSIZE):
        updateFly(i)

def main():
    # Init fishes
    for i in range(SWARMSIZE):
        swarmX.append(random() * 16)
        swarmY.append(random() * 16)

    # Draw plot
    while True:
        plt.cla()
        updateSwarm()
        plt.title('Swarm Simulation')
        plt.xlim(XLIM[0], XLIM[1])
        plt.ylim(YLIM[0], YLIM[1])
        plt.plot(swarmX, swarmY, '.')
        plt.draw()
        plt.pause(TICKRATE)

if __name__ == '__main__':
    main()
