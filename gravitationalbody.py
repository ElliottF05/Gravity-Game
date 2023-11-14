import math
import pygame

G = 100000
screenWidth = 0
screenHeight = 0

class GravitationalBody:

    bodies = []

    def __init__(self, mass, radius, xpos, ypos, xvel, yvel):
        self.mass = mass
        self.radius = radius
        self.xpos = xpos
        self.ypos = ypos
        self.xvel = xvel
        self.yvel = yvel
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


    # VISUALS

    def render(self, surface, zoom, cameraX, cameraY):
        relativeX = (self.xpos - cameraX) * zoom
        relativeY = (self.ypos - cameraY) * zoom
        pygame.draw.circle(surface, "green", self.toScreenCoords(relativeX, relativeY), 10)

    @classmethod
    def renderAll(cls, surface, zoom, cameraX, cameraY):
        for body in cls.bodies:
            body.render(surface, zoom, cameraX, cameraY)

    @staticmethod
    def toScreenCoords(x, y):
        return (screenWidth / 2 + x, screenHeight / 2 - y)