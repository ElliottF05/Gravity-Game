import math
from collections import deque

import pygame

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

    def __init__(self, xpos, ypos, xvel, yvel, mass, radius=10):
        self.xpos = xpos
        self.ypos = ypos
        self.xvel = xvel
        self.yvel = yvel
        self.mass = mass
        self.radius = radius
        self.trail = deque()
        self.futureTrail = deque()
        self.image = None
        self.bodies.append(self)


    # PHYSICS

    def vectorTo(self, other):
        x2 = other.xpos
        return other.xpos - self.xpos, other.ypos - self.ypos

    def distanceTo(self, other):
        return math.sqrt((other.xpos - self.xpos)**2 + (other.ypos - self.ypos)**2)

    def unitVectorTo(self, other):
        vectorTo = self.vectorTo(other)
        distanceTo = self.distanceTo(other)
        return (vectorTo[0] / distanceTo, vectorTo[1] / distanceTo)


    def gravityWith(self, other, deltaT):
        Fgrav_magnitude = G * self.mass * other.mass / self.distanceTo(other)**2
        unitVector = self.unitVectorTo(other)

        self.xvel += Fgrav_magnitude * unitVector[0] * deltaT / self.mass
        other.xvel -= Fgrav_magnitude * unitVector[0] * deltaT / other.mass

        self.yvel += Fgrav_magnitude * unitVector[1] * deltaT / self.mass
        other.yvel -= Fgrav_magnitude * unitVector[1] * deltaT / other.mass

    def updatePos(self, deltaT):
        self.xpos += self.xvel * deltaT
        self.ypos += self.yvel * deltaT

    @classmethod
    def calculateMotion(cls, fps, subUpdates):
        for k in range(subUpdates):
            for i in range(len(cls.bodies)):
                for j in range(i + 1, len(cls.bodies)):
                    cls.bodies[i].gravityWith(cls.bodies[j], 1 / (fps * subUpdates))
            for body in cls.bodies:
                body.updatePos(1 / (fps * subUpdates))
            if k % (subUpdates / trailUpdatesPerFrame) == 0:
                cls.updateTrails()


    # VISUALS

    def render(self, surface):
        pygame.draw.circle(surface, "green", toScreenCoords(self.futureTrail[0]), self.radius * zoom)

    def renderTrail(self, surface):
        for pos in self.trail:
            pygame.Surface.set_at(surface, toScreenCoords(pos), "white")

    def renderFutureTrail(self, surface):
        for pos in self.futureTrail:
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
            body.futureTrail.append((body.xpos, body.ypos))
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
            xSum += body.futureTrail[0][0]
            ySum += body.futureTrail[0][1]
            totalMass += body.mass
        return xSum / totalMass, ySum / totalMass


