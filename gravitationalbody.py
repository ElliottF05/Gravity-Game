from collections import deque
import math, pygame, time
import numpy as np

# Physics Constants
G = 100000

# Display Constants
screenWidth = 0
screenHeight = 0
trailDuration = 0
futureTrailDuration = 0
trailUpdatesPerFrame = 10
fps = 0
subUpdates = 10

# Camera values
cameraPos = np.array([0,0])
zoom = 1


# USEFUL FUNCTIONS

def updateCamera(newCameraPos, newZoom):
    global cameraPos, zoom
    cameraPos = newCameraPos
    zoom = newZoom


def toScreenCoords(coords): # converts coords with origin at center (physics based) to origin at top left
    return (int(screenWidth / 2 + (coords[0] - cameraPos[0]) * zoom)), int(screenHeight / 2 - (coords[1] - cameraPos[1]) * zoom)


# MAIN CLASS

class GravitationalBody:

    bodies = []

    def __init__(self, startPos , startVel, mass, radius=10):

        self.pos = np.array(startPos, dtype=np.float64)
        self.vel = np.array(startVel, dtype=np.float64)

        self.mass = mass
        self.radius = radius

        self.trail = deque()
        self.futureTrail = deque()

        self.image = None
        self.bodies.append(self)

        self.trail.append((self.pos, self.vel))


    # RETRIEVING VARIABLES

    def get_x_pos(self):
        return self.pos[0]
    def get_y_pos(self):
        return self.pos[1]
    def get_x_vel(self):
        return self.vel[0]
    def get_y_vel(self):
        return self.vel[1]


    # PHYSICS

    @classmethod
    def calculateMotion(cls):

        for k in range(subUpdates):

            for i in range(len(cls.bodies)):
                for j in range(i + 1, len(cls.bodies)):

                    cls.bodies[i].gravityWith(cls.bodies[j])

            for body in cls.bodies:
                deltaT = 1 / (fps * subUpdates)
                body.pos += body.vel * deltaT

            if k % (subUpdates / trailUpdatesPerFrame) == 0:
                for body in cls.bodies:
                    body.trail.append((np.copy(body.pos), np.copy(body.vel)))
                    if (len(body.trail)) > trailDuration * trailUpdatesPerFrame * 60:
                        body.trail.popleft()


    def gravityWith(self, other):
        deltaT = 1 / (fps * subUpdates)
        m1= self.mass
        m2 = other.mass
        r = other.pos - self.pos
        r_mag = np.linalg.norm(r)
        r_hat = r / r_mag

        Fgrav = G * m1 * m2 / r_mag**2 * r_hat

        self.vel += Fgrav * deltaT / m1
        other.vel -= Fgrav * deltaT / m2


    # VISUALS

    def render(self, surface):
        currentPos = self.pos
        pygame.draw.circle(surface, "green", toScreenCoords(currentPos), self.radius * zoom)

    def renderTrail(self, surface):
        for trailPoint in self.trail:
            pos = trailPoint[0]
            pygame.Surface.set_at(surface, toScreenCoords(pos), "white")

    @classmethod
    def renderBodies(cls, surface):
        for body in cls.bodies:
            body.render(surface)

    @classmethod
    def renderTrails(cls, surface):
        for body in cls.bodies:
            body.renderTrail(surface)

    @classmethod
    def getCenterOfMass(cls):
        cumulativePos = np.zeros(2)
        totalMass = 0
        for body in cls.bodies:
            cumulativePos += body.pos
            totalMass += body.mass
        return cumulativePos / totalMass


    # Control / Interaction Functions