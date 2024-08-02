from matplotlib import pyplot as plt
from random import sample
from numpy import sqrt, pi
from math import sin, cos
from numpy.random import random as rand

SWARMSIZE = 128
SPEED = 0.5
LOCALRANGE = 1.0
TIGHTRANGE = 0.25
BOUNDRANGE = 4.0
INITRANGEFRAC = 4

WEIGHTSELF = 5.0
WEIGHTLOCAL = 3.0
WEIGHTRAND = 2.0
WEIGHTATTRACTOR = 32.0
WEIGHTCENTER = 1.0
WEIGHTTIGHT = 20.0
WEIGHTBOUND = 10.0

TICKRATE = 0.025
XLIM = [-16, 16]
YLIM = [-16, 16]
ATTRACTORCOUNT = 1
attrcenter = [[0, 0]]
attrr = [10.0]
attrstep = pi / 128

# Swarm coords
swarmX = []
swarmY = []
# Swarm vectors
swarmVX = []
swarmVY = []
# Attractors
attr = [[4.0, 0.0]]
attrT = []

# Gen rand positive or negative (1 or -1)
def randpn():
    return rand() * sample([1, -1], k = 1)[0]

# Euclidian distance (2D)
def euclidDist(x0, y0, x1, y1):
    return sqrt((x0 - x1)**2 + (y0 - y1)**2)

# Update single fish
def updateFish(ind):
    d = 0.0
    ld = []
    lx = []
    ly = []
    lvx = []
    lvy = []
    tvx = 0.0
    tvy = 0.0
    weights = 0.0

    # Find local fishes
    for i in range(SWARMSIZE):
        if i == ind:
            continue
        if d := euclidDist(swarmX[ind], swarmY[ind], swarmX[i], swarmY[i]) <= LOCALRANGE:
            ld.append(d)
            lx.append(swarmX[i])
            ly.append(swarmY[i])
            lvx.append(swarmVX[i])
            lvy.append(swarmVY[i])
    # Find local TIGHT attrs
    for i in range(ATTRACTORCOUNT):
        if euclidDist(swarmX[ind], swarmY[ind], attr[i][0], attr[i][1]) <= TIGHTRANGE:
            tvx += -1 * (swarmX[ind] + attr[i][0]) / 2 * WEIGHTTIGHT
            tvy += -1 * (swarmY[ind] + attr[i][1]) / 2 * WEIGHTTIGHT
            weights += WEIGHTTIGHT

    # Weighted average

    # local
    for i, j in zip(lvx, lvy):
        tvx += i * WEIGHTLOCAL
        tvy += j * WEIGHTLOCAL
        weights += WEIGHTLOCAL
    # self
    tvx += swarmVX[ind] * WEIGHTSELF
    tvy += swarmVY[ind] * WEIGHTSELF
    weights += WEIGHTSELF
    # attr
    for i in range(ATTRACTORCOUNT):
        tvx += (attr[i][0] - swarmX[ind]) / euclidDist(swarmX[ind], swarmY[ind], attr[i][0], attr[i][1]) * WEIGHTATTRACTOR
        tvy += (attr[i][1] - swarmY[ind]) / euclidDist(swarmX[ind], swarmY[ind], attr[i][0], attr[i][1]) * WEIGHTATTRACTOR
        weights += WEIGHTATTRACTOR
    # local center
    lxs = 0
    lys = 0
    xylen = 0
    for i, j in zip(lx, ly):
        lxs += i
        lys += j
        xylen += 1
    if xylen != 0:
        lxs /= xylen
        lys /= xylen
        if euclidDist(swarmX[ind], swarmY[ind], lxs, lys) <= TIGHTRANGE:
            # tight
            tvx += -1 * (lxs - swarmX[ind]) / euclidDist(swarmX[ind], swarmY[ind], lxs, lys) * WEIGHTATTRACTOR
            tvy += -1 * (lys - swarmY[ind]) / euclidDist(swarmX[ind], swarmY[ind], lxs, lys) * WEIGHTATTRACTOR
        else:
            # center
            tvx += (lxs - swarmX[ind]) / euclidDist(swarmX[ind], swarmY[ind], lxs, lys) * WEIGHTATTRACTOR
            tvy += (lys - swarmY[ind]) / euclidDist(swarmX[ind], swarmY[ind], lxs, lys) * WEIGHTATTRACTOR
            weights += WEIGHTCENTER

    if weights != 0:
        tvx /= weights
        tvy /= weights

    # Give value
    swarmVX[ind] = tvx
    swarmVY[ind] = tvy
    swarmVX[ind] += randpn() * WEIGHTRAND
    swarmVY[ind] += randpn() * WEIGHTRAND

    # Move
    swarmX[ind] += swarmVX[ind] * SPEED
    swarmY[ind] += swarmVY[ind] * SPEED
    # Near bound: turn back
    if swarmX[ind] < XLIM[0] + BOUNDRANGE or swarmX[ind] > XLIM[1] - BOUNDRANGE:
        swarmVX[ind] *= -1 * WEIGHTBOUND
    if swarmY[ind] < YLIM[0] + BOUNDRANGE or swarmY[ind] > YLIM[1] - BOUNDRANGE:
        swarmVY[ind] *= -1 * WEIGHTBOUND

# Update whole swarm
def updateSwarm():
    for ind in range(SWARMSIZE):
        # Out of bound: rectify
        if swarmX[ind] < XLIM[0]:
            swarmX[ind] = XLIM[0] + BOUNDRANGE
        elif swarmY[ind] < YLIM[0]:
            swarmY[ind] = YLIM[0] + BOUNDRANGE
        elif swarmX[ind] > XLIM[1]:
            swarmX[ind] = XLIM[1] - BOUNDRANGE
        elif swarmY[ind] > YLIM[1]:
            swarmY[ind] = YLIM[1] - BOUNDRANGE
        # vector
        if swarmVX[ind] < XLIM[0]:
            swarmVX[ind] = XLIM[0]
        elif swarmVY[ind] < YLIM[0]:
            swarmVY[ind] = YLIM[0]
        elif swarmVX[ind] > XLIM[1]:
            swarmVX[ind] = XLIM[1]
        elif swarmVY[ind] > YLIM[1]:
            swarmVY[ind] = YLIM[1]
    for i in range(SWARMSIZE):
        updateFish(i)

def spinAttractor(ind):
    attrT[ind] += attrstep + rand() / 16
    attrr[ind] += randpn() / 8
    if attrT[ind] >= 2 * pi:
        attrT[ind] %= 2 * pi
    attr[ind][0] = cos(attrT[ind]) * attrr[ind] + randpn() / 8
    attr[ind][1] = sin(attrT[ind]) * attrr[ind] + randpn() / 8

def main():
    # Init fishes
    for i in range(SWARMSIZE):
        swarmX.append(XLIM[1] * randpn() / INITRANGEFRAC)
        swarmY.append(YLIM[1] * randpn() / INITRANGEFRAC)
        swarmVX.append(randpn())
        swarmVY.append(randpn())
    for i in range(ATTRACTORCOUNT):
        attrT.append(0.0)

    # Draw plot
    while True:
        plt.cla()
        updateSwarm()
        spinAttractor(0)
        plt.title('Swarm Simulation')
        plt.xlim(XLIM[0], XLIM[1])
        plt.ylim(YLIM[0], YLIM[1])
        plt.plot(swarmX, swarmY, 'b.')
        for i in range(ATTRACTORCOUNT):
            plt.plot(attr[i][0], attr[i][1], 'g.')
        plt.draw()
        plt.pause(TICKRATE)

if __name__ == '__main__':
    main()
