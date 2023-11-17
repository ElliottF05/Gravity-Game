import vectors
from vectors import *

from collections import deque
import math, pygame, time

# Physics Constants
G = 100000

# Display Constants
screenWidth = 0
screenHeight = 0
trailDuration = 0
futureTrailDuration = 0
trailUpdatesPerFrame = 10
fps = 0
subUpdates = 0

# Camera values
cameraPos = vec(0, 0)
zoom = 1

def updateCamera(newCameraPos, newZoom):
    global cameraPos, zoom
    cameraPos = newCameraPos
    zoom = newZoom


def toScreenCoords(coords): # converts coords with origin at center (physics based) to origin at top left
    return (int(screenWidth / 2 + (coords.x - cameraPos.x) * zoom)), int(screenHeight / 2 - (coords.y - cameraPos.y) * zoom)

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


    # PHYSICS

    @classmethod
    def calculateMotion(cls):
        for k in range(subUpdates):
            for i in range(len(cls.bodies)):
                for j in range(i + 1, len(cls.bodies)):
                    cls.bodies[i].gravityWith(cls.bodies[j])
            for body in cls.bodies:
                body.updateFrontPos(1 / (fps * subUpdates))
            if k % (subUpdates / trailUpdatesPerFrame) == 0:
                cls.updateTrails()

    def vectorToFront(self, other):
        return self.frontPos.vectorTo(other.frontPos)

    def vectorToCurrent(self, other):
        return self.getCurrentPos().vectorTo(other.getCurrentPos())

    def gravityWith(self, other):
        deltaT = 1 / (fps * subUpdates)
        Fgrav = (G * self.mass * other.mass / self.vectorToFront(other).mag()**2) * self.vectorToFront(other).unitVector()

        self.frontVel += Fgrav * deltaT / self.mass
        other.frontVel -= Fgrav * deltaT / other.mass


    def updateFrontPos(self, deltaT):
        self.frontPos += self.frontVel * deltaT

    @classmethod
    def recalculateFutureTrails(cls):
        for body in cls.bodies:
            body.frontPos = body.getCurrentPos()
            body.futureTrail = deque()
        for i in range(60 * futureTrailDuration - 1):
            cls.calculateMotion()

    # VISUALS

    def render(self, surface):
        currentPos = self.getCurrentPos()
        pygame.draw.circle(surface, "green", toScreenCoords(currentPos), self.radius * zoom)

    def renderTrail(self, surface):
        for t in self.trail:
            pos = t[0]
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
            xSum += body.getCurrentPos().x
            ySum += body.getCurrentPos().y
            totalMass += body.mass
        return vec(xSum, ySum) / totalMass


    # Control / Interaction Functions

    @classmethod
    def getNetGravityVector(cls, ship):
        netGravity = vec(0, 0)
        for body in cls.bodies:
            if body == ship:
                continue
            netGravity += (-G * body.mass * ship.mass / body.vectorToCurrent(ship).mag()**2) * body.vectorToCurrent(ship).unitVector()
        return netGravity