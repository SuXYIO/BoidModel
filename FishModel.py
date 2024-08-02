from matplotlib import pyplot as plt
from random import sample
from numpy import sqrt, pi
from math import sin, cos
from numpy.random import random as rand
from matplotlib.backend_bases import MouseButton as pltmouse

class dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class lim:
    def __init__(self, l, u):
        self.l = l
        self.u = u

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
XLIM = lim(-16, 16)
YLIM = lim(-16, 16)
ATTRACTORCOUNT = 1
attrcenter = [[0, 0]]
attrr = [10.0]
attrstep = pi / 128

# Swarm dots
swarm = []
# Swarm vectors
swarmV = []
# Attractors
attr = [dot(4, 0)]
attrT = []

# Interaction control
moveattr = False

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
        if d := euclidDist(swarm[ind].x, swarm[ind].y, swarm[i].x, swarm[i].y) <= LOCALRANGE:
            ld.append(d)
            lx.append(swarm[i].x)
            ly.append(swarm[i].y)
            lvx.append(swarmV[i].x)
            lvy.append(swarmV[i].y)
    # Find local TIGHT attrs
    for i in range(ATTRACTORCOUNT):
        if euclidDist(swarm[ind].x, swarm[ind].y, attr[i].x, attr[i].y) <= TIGHTRANGE:
            tvx += -1 * (swarm[ind].x + attr[i].x) / 2 * WEIGHTTIGHT
            tvy += -1 * (swarm[ind].y + attr[i].y) / 2 * WEIGHTTIGHT
            weights += WEIGHTTIGHT

    # Weighted average

    # local
    for i, j in zip(lvx, lvy):
        tvx += i * WEIGHTLOCAL
        tvy += j * WEIGHTLOCAL
        weights += WEIGHTLOCAL
    # self
    tvx += swarmV[ind].x * WEIGHTSELF
    tvy += swarmV[ind].y * WEIGHTSELF
    weights += WEIGHTSELF
    # attr
    for i in range(ATTRACTORCOUNT):
        tvx += (attr[i].x - swarm[ind].x) / euclidDist(swarm[ind].x, swarm[ind].y, attr[i].x, attr[i].y) * WEIGHTATTRACTOR
        tvy += (attr[i].y - swarm[ind].y) / euclidDist(swarm[ind].x, swarm[ind].y, attr[i].x, attr[i].y) * WEIGHTATTRACTOR
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
        if euclidDist(swarm[ind].x, swarm[ind].y, lxs, lys) <= TIGHTRANGE:
            # tight
            tvx += -1 * (lxs - swarm[ind].x) / euclidDist(swarm[ind].x, swarm[ind].y, lxs, lys) * WEIGHTATTRACTOR
            tvy += -1 * (lys - swarm[ind].y) / euclidDist(swarm[ind].x, swarm[ind].y, lxs, lys) * WEIGHTATTRACTOR
        else:
            # center
            tvx += (lxs - swarm[ind].x) / euclidDist(swarm[ind].x, swarm[ind].y, lxs, lys) * WEIGHTATTRACTOR
            tvy += (lys - swarm[ind].y) / euclidDist(swarm[ind].x, swarm[ind].y, lxs, lys) * WEIGHTATTRACTOR
            weights += WEIGHTCENTER

    if weights != 0:
        tvx /= weights
        tvy /= weights

    # Give value
    swarmV[ind].x = tvx
    swarmV[ind].y = tvy
    swarmV[ind].x += randpn() * WEIGHTRAND
    swarmV[ind].y += randpn() * WEIGHTRAND

    # Move
    swarm[ind].x += swarmV[ind].x * SPEED
    swarm[ind].y += swarmV[ind].y * SPEED
    # Near bound: turn back
    if swarm[ind].x < XLIM.l + BOUNDRANGE or swarm[ind].x > XLIM.u - BOUNDRANGE:
        swarmV[ind].x *= -1 * WEIGHTBOUND
    if swarm[ind].y < YLIM.l + BOUNDRANGE or swarm[ind].y > YLIM.u - BOUNDRANGE:
        swarmV[ind].y *= -1 * WEIGHTBOUND

# Update whole swarm
def updateSwarm():
    for ind in range(SWARMSIZE):
        # Out of bound: rectify
        if swarm[ind].x < XLIM.l:
            swarm[ind].x = XLIM.l + BOUNDRANGE
        elif swarm[ind].y < YLIM.l:
            swarm[ind].y = YLIM.l + BOUNDRANGE
        elif swarm[ind].x > XLIM.u:
            swarm[ind].x = XLIM.u - BOUNDRANGE
        elif swarm[ind].y > YLIM.u:
            swarm[ind].y = YLIM.u - BOUNDRANGE
        # vector
        if swarmV[ind].x < XLIM.l:
            swarmV[ind].x = XLIM.l
        elif swarmV[ind].y < YLIM.l:
            swarmV[ind].y = YLIM.l
        elif swarmV[ind].x > XLIM.u:
            swarmV[ind].x = XLIM.u
        elif swarmV[ind].y > YLIM.u:
            swarmV[ind].y = YLIM.u
    for i in range(SWARMSIZE):
        updateFish(i)

def spinAttractor(ind):
    attrT[ind] += attrstep + rand() / 16
    attrr[ind] += randpn() / 8
    if attrT[ind] >= 2 * pi:
        attrT[ind] %= 2 * pi
    attr[ind].x = cos(attrT[ind]) * attrr[ind] + randpn() / 8
    attr[ind].y = sin(attrT[ind]) * attrr[ind] + randpn() / 8

def on_move(event):
    if event.inaxes:
        global attr
        if moveattr == True:
            attr[0].x = event.xdata
            attr[0].y = event.ydata

def on_click(event):
    if event.button is pltmouse.LEFT:
        # toggle moveattr
        global moveattr
        if moveattr == False:
            moveattr = True
        else:
            moveattr = False

def main():
    # Init fishes
    for i in range(SWARMSIZE):
        swarm.append(dot(XLIM.u * randpn() / INITRANGEFRAC, YLIM.u * randpn() / INITRANGEFRAC))
        swarmV.append(dot(randpn(), randpn()))
    for i in range(ATTRACTORCOUNT):
        attrT.append(0.0)

    # Draw plot
    while True:
        #HACK: This does not support mutiple attractors
        binding_id = plt.connect('motion_notify_event', on_move)
        plt.connect('button_press_event', on_click)

        plt.cla()
        updateSwarm()
        if moveattr == False:
            spinAttractor(0)
        plt.title('Swarm Simulation')
        plt.xlim(XLIM.l, XLIM.u)
        plt.ylim(YLIM.l, YLIM.u)
        x_vals = [dot.x for dot in swarm]
        y_vals = [dot.y for dot in swarm]
        plt.plot(x_vals, y_vals, 'b-')
        for i in range(ATTRACTORCOUNT):
            plt.plot(attr[i].x, attr[i].y, 'g.')
        plt.draw()
        plt.pause(TICKRATE)

if __name__ == '__main__':
    main()
