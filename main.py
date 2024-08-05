from random import sample, random
import math

import turtle as tur
import logging

from matplotlib.colors import BoundaryNorm

# point (2d)
class pnt:
    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y

# vector (2d)
class vec:
    def __init__(self, x = 0.0, y = 0.0):
        self.x = x
        self.y = y

# limitation for 2d space
class lim:
    def __init__(self, xl, xu, yl, yu):
        self.xl = xl
        self.xu = xu
        self.yl = yl
        self.yu = yu

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

TICKRATE = 0.1
INITRANGEFRAC = 1
VECMAX = math.sqrt(1 / 2)
LIM = lim(-8, 8, -8, 8)

SWMSIZE = 64
SPEED = 0.5

LOCALRANGE = 1.0
SEPRANGE = 0.6

WOLD = 0.8
WSEP = 1.0
WCOH = 1.0
WALI = 1.0
WRND = 0.5

# Swarm pnts
swm = []
# Swarm vectors
swmv = []

# Misc
pen = []

# Options
# show method ('matplotlib' / 'pygame')
showmethod = 'matplotlib'
# bound method ('wrap' / 'bounce')
boundmethod = 'bounce'
# Plot local for every fish
#TEST: This might greatly reduce performance
localplot = False

if showmethod == 'matplotlib':
    from matplotlib import use as pltuse
    from matplotlib import pyplot as plt
    from matplotlib.backend_bases import MouseButton
elif showmethod == 'pygame':
    import pygame
    COLORPNT = (0, 0, 255)
    COLORBG = (0, 0, 0)
else:
    logging.error(f'Invalid show method: {showmethod}')
    exit()

def randpn():
    """Gen rand positive or negative (1 or -1)"""
    return random() * sample([1, -1], k = 1)[0]

def euclidDist(p0, p1):
    """Euclidian distance (2D)"""
    return math.sqrt((p0.x - p1.x)**2 + (p0.y - p1.y)**2)

def meanPnt(pntlist):
    """Average pnt of pnt list"""
    mean = pnt()
    for i in pntlist:
        mean.x += i.x
        mean.y += i.y
    mean.x /= len(pntlist)
    mean.y /= len(pntlist)
    return mean

def meanPntW(pntlist, weightlist):
    """Weighted average pnt of pnt list"""
    mean = pnt()
    wsum = 0.0
    for i in range(len(pntlist)):
        mean.x += pntlist[i].x * weightlist[i]
        mean.y += pntlist[i].y * weightlist[i]
        wsum += weightlist[i]
    mean.x /= wsum
    mean.y /= wsum
    return mean

def relVec(p0, p1):
    """Relative vector from point to point (2d)"""
    return pnt(p1.x - p0.x, p1.y - p0.y)

def modVec(v):
    """The module(length) of vector (2d)"""
    return math.sqrt(v.x**2 + v.y**2)

def headVec(v):
    """Calc the heading of vector (2d)"""
    return math.degrees(math.atan2(v.y, v.x))

# Update single bird
def updateBird(ind, plotmethod):
    # Init
    # define values
    localswm = []
    localswmv = []
    localdist = []
    # define forces
    forceold = swmv[ind]
    forcesep = vec()
    forcecoh = vec()
    forceali = vec()
    forcerand = vec()

    # Find local
    #TODO: Use quad-tree search to reduce time complicity from O(n) to O(log n)
    for i in range(SWMSIZE):
        # Skip self
        if i == ind:
            continue
        if d := euclidDist(swm[ind], swm[i]):
            localswm.append(swm[i])
            localswmv.append(swmv[i])
            localdist.append(d)

    # Separate
    # find the min of local dist
    mindist = min(localdist)
    # find the pnts of min dist
    minpnt = localswm[localdist.index(mindist)]
    # calc relative vec to minpnt
    relminpnt = relVec(swm[ind], minpnt)
    # add force with n / d^2
    fmindist = SEPRANGE / mindist**2
    forcesep.x = relminpnt.x * fmindist
    forcesep.y = relminpnt.y * fmindist

    # Cohesion
    # calc avg point of local
    avglocalpnt = meanPnt(localswm)
    # calc relative vec to avgpnt
    forcecoh = relVec(swm[ind], avglocalpnt)

    # Align
    # calc averge vec for local
    avglocalswmv = meanPnt(localswmv)
    forceali = meanPnt([swmv[ind], avglocalswmv])

    # Random
    forcerand = vec(randpn(), randpn())

    # Update own vector
    # new vec = average of the forces
    swmv[ind] = meanPntW(
        [forceold,  forcesep,   forcecoh,   forceali,   forcerand], 
        [WOLD,      WSEP,       WCOH,       WALI,       WRND]
    )

    # Move toward vector
    swm[ind].x += swmv[ind].x * SPEED
    swm[ind].y += swmv[ind].y * SPEED

    # Bound
    if boundmethod == 'wrap':
        # wrap coords (appear on the other side)
        SHIFT = random() * 0.0
        if swm[ind].x < LIM.xl:
            swm[ind].x = LIM.xu - SHIFT
        if swm[ind].y < LIM.yl:
            swm[ind].y = LIM.yu - SHIFT
        if swm[ind].x > LIM.xu:
            swm[ind].x = LIM.xl + SHIFT
        if swm[ind].y > LIM.yu:
            swm[ind].y = LIM.yl + SHIFT
    elif boundmethod == 'bounce':
        if swm[ind].x < LIM.xl:
            swmv[ind].x = abs(swmv[ind].x)
        elif swm[ind].x > LIM.xu:
            swmv[ind].x = -abs(swmv[ind].x)
        if swm[ind].y < LIM.yl:
            swmv[ind].y = abs(swmv[ind].y)
        elif swm[ind].y > LIM.yu:
            swmv[ind].y = -abs(swmv[ind].y)

    # Localplot
    global localplot
    if localplot == True:
        if plotmethod == 'matplotlib':
            #TODO: Reduce duplicate lines
            localx_vals = [pnt.x for pnt in localswm]
            localy_vals = [pnt.y for pnt in localswm]
            plt.plot(localx_vals, localy_vals, 'b.-')
        elif plotmethod == 'pygame':
            pass

# Update whole boid
def updateBoid(plotmethod):
    for ind in range(SWMSIZE):
        updateBird(ind, plotmethod)

# Click event
def on_click(event):
    if event.button is MouseButton.LEFT:
        # Toggle plot local
        global localplot
        localplot = not localplot
        print(f'localplot = {localplot}')

def main():
    # Init fishes
    for i in range(SWMSIZE):
        swm.append(pnt(LIM.xu * randpn() / INITRANGEFRAC, LIM.yu * randpn() / INITRANGEFRAC))
        swmv.append(vec(randpn() * VECMAX, randpn() * VECMAX))

    # Draw plot
    if showmethod == 'matplotlib':
        pltuse('TkAgg')
        plt.connect('button_press_event', on_click) 
        while True:
            plt.cla()
            updateBoid('matplotlib')
            plt.title('Swarm Simulation')
            plt.xlim(LIM.xl, LIM.xu)
            plt.ylim(LIM.yl, LIM.yu)
            x_vals = [pnt.x for pnt in swm]
            y_vals = [pnt.y for pnt in swm]
            if localplot == False:
                plt.scatter(x_vals, y_vals, c = 'b', marker = '^')
            plt.draw()
            plt.pause(TICKRATE)
    elif showmethod == 'pygame':
        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Swarm Simulation')
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill(COLORBG)

            # Update the swarm
            updateBoid('pygame')
            # Draw the swarm
            for boid, boidv in zip(swm, swmv):
                # Calculate the angle of the velocity vector
                angle = headVec(boidv)
                # Create a surface for the boid
                boid_surface = pygame.Surface((10, 10))
                boid_surface.set_colorkey((0, 0, 0))
                boid_surface.fill((0, 0, 0))
                points = [(5, 0), (8, 5), (2, 5)]
                rotated_points = []
                for point in points:
                    rotated_x = point[0] - 5
                    rotated_y = point[1] - 5
                    new_x = rotated_x * math.cos(angle) - rotated_y * math.sin(angle) + 5
                    new_y = rotated_x * math.sin(angle) + rotated_y * math.cos(angle) + 5
                    rotated_points.append((new_x, new_y))
                pygame.draw.polygon(boid_surface, (255, 255, 255), rotated_points)
                # Draw the rotated surface
                SCALE = 50
                screen.blit(boid_surface, (int(boid.x * SCALE + SCREEN_WIDTH / 2 - 5), int(boid.y * SCALE + SCREEN_HEIGHT / 2 - 5)))

            # Update the display
            pygame.display.flip()
            # Cap the frame rate
            pygame.time.delay(int(TICKRATE * 1000))
            clock.tick(60)
        # Quit Pygame
        pygame.quit()
    else:
        logging.error(f'Unknown plotmethod: {plotmethod}. ')
    exit()

if __name__ == '__main__':
    main()
    exit()

