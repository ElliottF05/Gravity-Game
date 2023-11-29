from collections import deque

import math, pygame, time

import numpy as np

from numba import njit

# Physics Constants
G = 100000

max_deltaT = 1.0 / 60.0
min_deltaT = 1.0 / (60.0 * 20.0)

# Display Constants
screenWidth = 0
screenHeight = 0
trailDuration = 0
futureTrailUpdates = 0
fps = 0
subUpdates = 0
timeStepsPerTrailPoint = 0

# Camera values
cameraPos = np.array([0,0])
zoom = 1


# USEFUL FUNCTIONS

def updateCamera(newCameraPos, newZoom):
    global cameraPos, zoom
    cameraPos = newCameraPos
    zoom = newZoom


def toScreenCoords(coords): # converts coords with origin at center (physics based) to origin at top left
    if (math.isnan(coords[0]) or math.isnan(coords[1]) or max(abs(coords[0]), abs(coords[1])) > 10**9):
        return (2 * screenWidth, 2 * screenHeight)
    return (int(screenWidth / 2 + (coords[0] - cameraPos[0]) * zoom)), int(screenHeight / 2 - (coords[1] - cameraPos[1]) * zoom)


# MAIN CLASS

class GravitationalBody:

    bodies = []

    def __init__(self, startPos , startVel, mass, radius=10, color="green"):

        self.pos = np.array(startPos, dtype=np.float64)
        self.vel = np.array(startVel, dtype=np.float64)
        # self.accel = np.zeros(2)

        self.mass = mass
        self.radius = radius

        self.trail = deque()
        self.futureTrail = deque()

        self.color = color
        self.bodies.append(self)

        self.trail.append(self.pos)


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

            if k % (subUpdates) == 0:
                for body in cls.bodies:
                    body.trail.append(np.copy(body.pos))
                    if (len(body.trail)) > trailDuration * 60:
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


    @staticmethod
    @njit
    def numbaFutureTrails(bodyData, futureTrailData):

        futureTrailPos = 0

        for update in range(futureTrailUpdates):

            for i in range(np.shape(bodyData)[0]):
                bodyData[i][5] = 0
                bodyData[i][6] = 0

            for i in range(np.shape(bodyData)[0]):
                body1 = bodyData[i]
                m1 = body1[4]
                body1x, body1y = body1[0], body1[1]
                for j in range(i + 1, np.shape(bodyData)[0]):
                    body2 = bodyData[j]
                    m2 = body2[4]
                    body2x, body2y = body2[0], body2[1]

                    rx = body2x - body1x
                    ry = body2y - body1y
                    r_mag = math.sqrt(rx ** 2 + ry ** 2)
                    r_hat_x = rx / r_mag
                    r_hat_y = ry / r_mag

                    Fgrav_mag = G * m1 * m2 / r_mag ** 2
                    Fgrav_x = Fgrav_mag * r_hat_x
                    Fgrav_y = Fgrav_mag * r_hat_y

                    # updating acceleration
                    body1[5] += Fgrav_x / m1
                    body1[6] += Fgrav_y / m1
                    body2[5] -= Fgrav_x / m2
                    body2[6] -= Fgrav_y / m2

            maxAccel_mag = 0
            for i in range(np.shape(bodyData)[0]):
                maxAccel_mag = max(maxAccel_mag, math.sqrt(bodyData[i][5]**2 + bodyData[i][6]**2))
            deltaT = 1 / (maxAccel_mag * 1)
            deltaT = max(min_deltaT, deltaT)
            deltaT = min(max_deltaT, deltaT)
            deltaT = 1.0 / (60.0 * math.ceil((1.0 / 60.0) / deltaT)) # rounds deltaT to integer quotient of 1/60 e.g (1/60) / 10
            # deltaT = 1 / (fps * subUpdates)

            for i in range(np.shape(bodyData)[0]):
                bodyData[i][2] += bodyData[i][5] * deltaT
                bodyData[i][3] += bodyData[i][6] * deltaT

            for i in range(np.shape(bodyData)[0]):
                bodyData[i][0] += bodyData[i][2] * deltaT
                bodyData[i][1] += bodyData[i][3] * deltaT

            if update % timeStepsPerTrailPoint == 0:
                for bodyPos in range(np.shape(bodyData)[0]):
                    futureTrailData[bodyPos][futureTrailPos] = np.array([bodyData[bodyPos][0], bodyData[bodyPos][1]])
                futureTrailPos += 1


    @classmethod
    def calculateFutureTrails(cls):
        # creating data to be used by numba
        bodyData = np.empty( (len(cls.bodies), 7) )  # format is [body][xpos, ypos, xvel, yvel, mass, accel_x, accel_y]
        futureTrailData = np.empty( (len(cls.bodies), int(futureTrailUpdates / timeStepsPerTrailPoint), 2) )  # format is [body][trailPoint][xpos, ypos]

        for i in range(len(cls.bodies)):
            body = cls.bodies[i]
            bodyData[i] = np.array([body.pos[0], body.pos[1], body.vel[0], body.vel[1], body.mass, 0, 0])

        cls.numbaFutureTrails(bodyData, futureTrailData)

        for i in range(len(cls.bodies)):
            cls.bodies[i].futureTrail = deque(futureTrailData[i])


    # VISUALS

    def render(self, surface):
        currentPos = self.pos
        pygame.draw.circle(surface, self.color, toScreenCoords(currentPos), self.radius * zoom)

    def renderTrail(self, surface):
        pygame.draw.aalines(surface, "white", False, [toScreenCoords(pos) for pos in self.trail])

    def renderFutureTrail(self, surface):
        pygame.draw.aalines(surface, (100, 100, 100), False, [toScreenCoords(pos) for pos in self.futureTrail])

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
    def getCenterOfMass(cls):
        cumulativePos = np.zeros(2)
        totalMass = 0
        for body in cls.bodies:
            cumulativePos += body.pos * body.mass
            totalMass += body.mass
        return cumulativePos / totalMass