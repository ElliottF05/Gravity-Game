import math
from collections import deque

import pygame

G = 100000
screenWidth = 0
screenHeight = 0
trailDuration = 0
trailUpdatePerFrame = 10

@staticmethod  # converts coords with origin at center (physics based) to origin at top left
def toScreenCoords(coords):
    return (int(screenWidth / 2 + coords[0]), int(screenHeight / 2 - coords[1]))

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
        self.image = None
        self.bodies.append(self)


    # PHYSICS

    def vectorTo(self, other):
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
            if k % (subUpdates / trailUpdatePerFrame) == 0:
                cls.updateTrail()


    # VISUALS

    def render(self, surface, zoom, cameraX, cameraY):
        for pos in self.trail:
            pygame.Surface.set_at(surface, toScreenCoords(pos), "white")
        relativeX = (self.xpos - cameraX) * zoom  # based on zoom and camera pos
        relativeY = (self.ypos - cameraY) * zoom  # based on zoom and camera pos
        pygame.draw.circle(surface, "green", toScreenCoords((relativeX, relativeY)), self.radius)

    @classmethod
    def renderAll(cls, surface, zoom, cameraX, cameraY):
        for body in cls.bodies:
            body.render(surface, zoom, cameraX, cameraY)

    @classmethod
    def updateTrail(cls):
        for body in cls.bodies:
            body.trail.appendleft((body.xpos, body.ypos))
            if len(body.trail) > 60 * trailDuration * trailUpdatePerFrame:
                pass
                body.trail.pop()

