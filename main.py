from matplotlib.backend_bases import MouseButton
from matplotlib import pyplot as plt
from random import sample, random
from math import sqrt, tanh, sin, cos, pi

class pnt:
    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y

class lim:
    def __init__(self, l, u):
        self.l = l
        self.u = u

TICKRATE = 0.0125
XLIM = lim(-8, 8)
YLIM = lim(-8, 8)

SWARMSIZE = 128
SPEED = 0.2
ATTRSPEED = 0.45
INITRANGEFRAC = 1

localrange = 1.0
TIGHTRANGE = 0.8
BOUNDRANGE = 2.0
ATTRCENTERFORCEMINDIST = XLIM.u * 3 / 4

WEIGHTLOCALCENTER = 1.5
WEIGHTLOCALVECTOR = 1.0
WEIGHTSELFVECTOR = 1.5
WEIGHTLOCALTIGHT = -3.0
WEIGHTRAND = 3.0
WEIGHTATTR = 0.5

WEIGHTATTRCENTER = 1

RANDTURNFRAC = 1 / 8
ATTRRANDTURNFRAC = 1 / 1
ATTRBOUNDRAD = 0.9
ATTRMAXRAD = 2.0
SHIFTFRAC = 2.0
ATTRSHIFTFRAC = 4.0

RECTIFYFUNCTION = lambda x: tanh(x) * 2
ATTRRECTIFYFUNCTION = lambda x: x

# Swarm pnts
swarm = []
# Swarm vectors
swarmV = []
# Attractor
attr = pnt()
attrV = pnt()

# Options
# Plot local for every fish
#TEST: This might greatly reduce performance
localplot = False
enableattr = False

# Gen rand positive or negative (1 or -1)
def randpn():
    return random() * sample([1, -1], k = 1)[0]

# Euclidian distance (2D)
def euclidDist(x0, y0, x1, y1):
    return sqrt((x0 - x1)**2 + (y0 - y1)**2)

# Update single fish
def updateFish(ind):
    #TEST: Experimental random localrange
    #localrange = random() * 2
    localswm = []
    localvec = []
    localdist = []
    tightswm = []
    tightdist = []
    localcnt = 0
    tightcnt = 0

    # Get local
    for i in range(SWARMSIZE):
        # skip self
        if i == ind:
            continue
        if d := euclidDist(swarm[ind].x, swarm[ind].y, swarm[i].x, swarm[i].y) <= localrange:
            localswm.append(swarm[i])
            localvec.append(swarmV[i])
            localdist.append(d)
            localcnt += 1
            if d <= TIGHTRANGE:
                tightswm.append(swarm[i])
                tightdist.append(d)
                tightcnt += 1

    # Plot local
    if localplot == True:
        localx_vals = [pnt.x for pnt in localswm]
        localy_vals = [pnt.y for pnt in localswm]
        plt.plot(localx_vals, localy_vals, 'b.-')

    # Calc local stuff
    # local center point
    centpt = pnt()
    # local average vector
    avgvec = pnt()
    # relative vector to local center
    relcentvec = pnt()
    # tight center point
    tightpt = pnt()
    # relative vector to tight center
    reltightvec = pnt()
    # local
    if localcnt > 0:
        for i in range(localcnt):
            centpt.x += localswm[i].x * localdist[i]
            centpt.y += localswm[i].y * localdist[i]
            avgvec.x += localvec[i].x
            avgvec.y += localvec[i].y
        centpt.x /= localcnt
        centpt.y /= localcnt
        avgvec.x /= localcnt
        avgvec.y /= localcnt
        relcentvec.x = (centpt.x - swarm[ind].x)
        relcentvec.y = (centpt.y - swarm[ind].y)
    # tight
    if tightcnt > 0:
        for i in range(tightcnt):
            tightpt.x += tightswm[i].x * 1 / tightdist[i]
            tightpt.y += tightswm[i].y * 1 / tightdist[i]
        tightpt.x /= tightcnt
        tightpt.y /= tightcnt
        reltightvec.x = (tightpt.x - swarm[ind].x)
        reltightvec.y = (tightpt.y - swarm[ind].y)

    # Attractor force
    attrdist = euclidDist(swarm[ind].x, swarm[ind].y, attr.x, attr.y)
    attrvec = pnt()
    if attrdist != 0:
        if attrdist <= ATTRBOUNDRAD:
            # distract
            attrvec.x = -(attr.x - swarm[ind].x) / attrdist
            attrvec.y = -(attr.y - swarm[ind].y) / attrdist
        elif attrdist >= ATTRMAXRAD:
            # attract
            attrvec.x = (attr.x - swarm[ind].x) * attrdist
            attrvec.y = (attr.y - swarm[ind].y) * attrdist

    # Random vector
    randvec = pnt(tanh(randpn()), tanh(randpn()))

    # Adjust own vector
    weightsum = 0.0
    swarmV[ind].x *= WEIGHTSELFVECTOR
    swarmV[ind].y *= WEIGHTSELFVECTOR
    swarmV[ind].x += relcentvec.x * WEIGHTLOCALCENTER
    swarmV[ind].y += relcentvec.y * WEIGHTLOCALCENTER
    swarmV[ind].x += avgvec.x * WEIGHTLOCALVECTOR
    swarmV[ind].y += avgvec.y * WEIGHTLOCALVECTOR
    swarmV[ind].x += reltightvec.x * WEIGHTLOCALTIGHT
    swarmV[ind].y += reltightvec.y * WEIGHTLOCALTIGHT
    swarmV[ind].x += randvec.x * WEIGHTRAND
    swarmV[ind].y += randvec.y * WEIGHTRAND
    weightsum += WEIGHTSELFVECTOR + WEIGHTLOCALCENTER + WEIGHTLOCALVECTOR + WEIGHTLOCALTIGHT
    if enableattr == True:
        swarmV[ind].x += attrvec.x * WEIGHTATTR
        swarmV[ind].y += attrvec.y * WEIGHTATTR
        weightsum += WEIGHTATTR
    # sub to weighted sum
    if weightsum > 0:
        swarmV[ind].x /= weightsum
        swarmV[ind].y /= weightsum

    # Vector rectify
    swarmV[ind].x = RECTIFYFUNCTION(swarmV[ind].x)
    swarmV[ind].y = RECTIFYFUNCTION(swarmV[ind].y)

    # Vector turn
    thetax = random() * ATTRRANDTURNFRAC
    thetay = random() * ATTRRANDTURNFRAC
    vx1 = swarmV[ind].x * cos(thetax) - swarmV[ind].y * sin(thetax)
    vy1 = swarmV[ind].x * sin(thetay) + swarmV[ind].y * cos(thetay)
    swarmV[ind].x = vx1
    swarmV[ind].y = vy1

    # Move
    swarm[ind].x += swarmV[ind].x * SPEED
    swarm[ind].y += swarmV[ind].y * SPEED

# Update whole swarm
def updateSwarm():
    for ind in range(SWARMSIZE):
        # Out of bound: reverse coords (finite universe)
        SHIFT = random() * 4.0
        # -
        if swarm[ind].x < XLIM.l:
            swarm[ind].x = XLIM.u - SHIFT
        if swarm[ind].y < YLIM.l:
            swarm[ind].y = YLIM.u - SHIFT
        # +
        if swarm[ind].x > XLIM.u:
            swarm[ind].x = XLIM.l + SHIFT
        if swarm[ind].y > YLIM.u:
            swarm[ind].y = YLIM.l + SHIFT
        updateFish(ind)

# Update attractor
#WARN: Might not adapt to new XLIM and YLIMs
#BUG: Attr point move incorrect
def updateAttr():
    # Vector turn
    theta = randpn() * pi * ATTRRANDTURNFRAC
    v1 = pnt()
    v1.x = attrV.x * cos(theta) - attrV.y * sin(theta)
    v1.y = attrV.x * sin(theta) + attrV.y * cos(theta)

    # Center rectify
    cent = pnt(XLIM.u + XLIM.l, YLIM.u + YLIM.l)
    '''
    # Turn
    if euclidDist(attr.x, attr.y, cent.x, cent.y) > ATTRCENTERFORCEMINDIST:
        theta = pi / 2
        vx1 += attrV.x * cos(theta) - attrV.y * sin(theta)
        vy1 += attrV.x * sin(theta) + attrV.y * cos(theta)
    '''
    # Center force
    centdist = euclidDist(attr.x, attr.y, cent.x, cent.y)
    relcentvec = pnt(cent.x - attr.x, cent.y - attr.y)
    relcentvec.x *= WEIGHTATTRCENTER 
    relcentvec.y *= WEIGHTATTRCENTER

    attrV.x += relcentvec.x
    attrV.y += relcentvec.y

    attrV.x = v1.x
    attrV.y = v1.y

    # Vector rectify
    attrV.x = ATTRRECTIFYFUNCTION(attrV.x)
    attrV.y = ATTRRECTIFYFUNCTION(attrV.y)

    # Move
    attr.x += attrV.x * ATTRSPEED
    attr.y += attrV.y * ATTRSPEED

    # Out of bound: reverse coords (finite universe)
    SHIFT = random() * SHIFTFRAC
    # -
    if attr.x < XLIM.l:
        attr.x = XLIM.u - SHIFT
    if attr.y < YLIM.l:
        attr.y = YLIM.u - SHIFT
    # +
    if attr.x > XLIM.u:
        attr.x = XLIM.l + SHIFT
    if attr.y > YLIM.u:
        attr.y = YLIM.l + SHIFT

# Click event
def on_click(event):
    if event.button is MouseButton.LEFT:
        # Toggle plot local
        global localplot
        localplot = not localplot
    elif event.button is MouseButton.RIGHT:
        # Toggle attractor force
        global enableattr
        enableattr = not enableattr

def main():
    # Init fishes
    #TEST: Might correct vector
    vecmax = sqrt(1 / 2)
    for i in range(SWARMSIZE):
        swarm.append(pnt(XLIM.u * randpn() / INITRANGEFRAC, YLIM.u * randpn() / INITRANGEFRAC))
        swarmV.append(pnt(randpn() * vecmax, randpn() * vecmax))
    attr.x = randpn()
    attr.y = randpn()
    attrV.x = randpn()
    attrV.y = randpn()

    plt.connect('button_press_event', on_click) 

    # Draw plot
    while True:
        plt.cla()
        updateSwarm()
        if enableattr == True:
            updateAttr()
        plt.title('Swarm Simulation')
        plt.xlim(XLIM.l, XLIM.u)
        plt.ylim(YLIM.l, YLIM.u)
        x_vals = [pnt.x for pnt in swarm]
        y_vals = [pnt.y for pnt in swarm]
        plt.xlabel(f'localPlot = {localplot}, attractorForce = {enableattr}')
        if localplot == False:
            plt.plot(x_vals, y_vals, 'b^')
        if enableattr == True:
            plt.plot(attr.x, attr.y, 'g.')
        plt.draw()
        plt.pause(TICKRATE)

if __name__ == '__main__':
    main()

