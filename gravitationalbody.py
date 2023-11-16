import vectors
from vectors import *

from collections import deque
import math, pygame

# Physics Constants
G = 100000

# Display Constants
screenWidth = 0
screenHeight = 0
trailDuration = 0
futureTrailDuration = 0
trailUpdatesPerFrame = 10

# Camera values
cameraX = 0
cameraY = 0
zoom = 1

def updateCamera(newCameraX, newCameraY, newZoom):
    global cameraX, cameraY, zoom
    cameraX = newCameraX
    cameraY = newCameraY
    zoom = newZoom


def toScreenCoords(coords): # converts coords with origin at center (physics based) to origin at top left
    x = coords[0]
    y = coords[1]
    return (int(screenWidth / 2 + (x - cameraX) * zoom)), int(screenHeight / 2 - (y - cameraY) * zoom)

class GravitationalBody:

    bodies = []

    def __init__(self, startPos , startVel, mass, radius=10):
        self.mass = mass
        self.radius = radius

        self.trail = deque()
        self.futureTrail = deque()

        self.image = None
        self.bodies.append(self)

        self.frontPos = startPos
        self.frontVel = startVel

        self.futureTrail.append((startPos, startVel))


    # RETRIEVING VARIABLES

    def getCurrentPos(self):
        return self.futureTrail[0][0]

    def getCurrentVel(self):
        return self.futureTrail[0][1]


    # MODIFYING VARIABLES

    def updateTrails(self):
        pass


    # PHYSICS

    @classmethod
    def calculateMotion(cls, fps, subUpdates):
        for k in range(subUpdates):
            for i in range(len(cls.bodies)):
                for j in range(i + 1, len(cls.bodies)):
                    cls.bodies[i].gravityWith(cls.bodies[j], 1 / (fps * subUpdates))
            for body in cls.bodies:
                body.updateFrontPos(1 / (fps * subUpdates))
            if k % (subUpdates / trailUpdatesPerFrame) == 0:
                cls.updateTrails()

    def gravityWith(self, other, deltaT):
        Fgrav_magnitude = G * self.mass * other.mass / mag(vectorBetween(self.frontPos, other.frontPos))**2
        unitVector = norm(vectorBetween(self.frontPos, other.frontPos))

        delta_xvel_self = Fgrav_magnitude * unitVector[0] * deltaT / self.mass
        delta_yvel_self = Fgrav_magnitude * unitVector[1] * deltaT / self.mass

        delta_xvel_other = Fgrav_magnitude * unitVector[0] * deltaT / other.mass
        delta_yvel_other = Fgrav_magnitude * unitVector[1] * deltaT / other.mass

        self.frontVel = (self.frontVel[0] + delta_xvel_self, self.frontVel[1] + delta_yvel_self)
        other.frontVel = (other.frontVel[0] - delta_xvel_other, other.frontVel[1] - delta_yvel_other)


    def updateFrontPos(self, deltaT):
        x, y = self.frontPos[0], self.frontPos[1]
        xvel, yvel = self.frontVel[0], self.frontVel[1]

        self.frontPos = (x + xvel * deltaT, y + yvel * deltaT)


    # VISUALS

    def render(self, surface):
        pygame.draw.circle(surface, "green", toScreenCoords(self.getCurrentPos()), self.radius * zoom)

    def renderTrail(self, surface):
        for trailState in self.trail:
            pos = trailState[0]
            pygame.Surface.set_at(surface, toScreenCoords(pos), "white")

    def renderFutureTrail(self, surface):
        for t in self.futureTrail:
            pos = t[0]
            pygame.Surface.set_at(surface, toScreenCoords(pos), (40, 40, 40))

    @classmethod
    def renderBodies(cls, surface):
        for body in cls.bodies:
            body.render(surface)

    @classmethod
    def renderTrails(cls, surface):
        for body in cls.bodies:
            body.renderTrail(surface)

    @classmethod
    def renderFutureTrails(cls, surface):
        for body in cls.bodies:
            body.renderFutureTrail(surface)

    @classmethod
    def updateTrails(cls):
        for body in cls.bodies:
            body.futureTrail.append((body.frontPos, body.frontVel))
            if len(body.futureTrail) > 60 * futureTrailDuration * trailUpdatesPerFrame:
                body.trail.append(body.futureTrail.popleft())
            if len(body.trail) > 60 * trailDuration * trailUpdatesPerFrame:
                body.trail.popleft()

    @classmethod
    def getCenterOfMass(cls):
        xSum = 0
        ySum = 0
        totalMass = 0
        for body in cls.bodies:
            xSum += body.getCurrentPos()[0]
            ySum += body.getCurrentPos()[1]
            totalMass += body.mass
        return xSum / totalMass, ySum / totalMass