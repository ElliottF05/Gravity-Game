from collections import deque

import math, pygame, time

import numpy as np

from numba import njit

# Physics Constants
G = 100000

MAX_DELTAT_LIVE = 1 * 1.0 / (60.0)
MAX_DELTAT_FUTURE = 1 * 1.0 / (60.0)
MIN_DELTAT = 1.0 / (60.0 * 100.0)

DELTAT_ACCEL_DIVISOR = 5

CLOSEST_DISTANCE = 3


# Display Constants

trailDuration = 1
futureTrailUpdates = 10000
timeStepsPerTrailPoint = 10

screenWidth = 0
screenHeight = 0


# Camera values

cameraPos = np.array([0,0])
cameraMode = 0
cameraBodyFocus = False
zoom = 1


# Physics Variables


# USEFUL FUNCTIONS

def updateCamera(newCameraPos, newZoom, newCameraMode, newCameraBodyFocus):
    global cameraPos, zoom, cameraMode, cameraBodyFocus
    cameraPos = newCameraPos
    zoom = newZoom
    cameraMode = newCameraMode
    cameraBodyFocus = newCameraBodyFocus


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
        self.accel = np.zeros(2)

        self.mass = mass
        self.radius = radius

        self.trail = deque()
        self.futureTrail = deque()

        self.color = color
        self.bodies.append(self)

        self.trail.append(self.pos)


    # PHYSICS

    @staticmethod
    @njit
    def numbaLiveMotion(bodyData):
        time_elapsed = 0
        while time_elapsed < 1.0 / 60.0:

            use_mindeltat = False
            for i in range(np.shape(bodyData)[0]):
                # setting accel to 0
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
                    if r_mag < CLOSEST_DISTANCE:
                        use_mindeltat = True
                        continue
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

            max_accel_for_vel = 0
            for i in range(np.shape(bodyData)[0]):
                max_accel_for_vel = max(max_accel_for_vel, math.sqrt(bodyData[i][5] ** 2 + bodyData[i][6] ** 2) / math.sqrt(bodyData[i][2] ** 2 + bodyData[i][3] ** 2))
            deltaT = 1 / (max_accel_for_vel * DELTAT_ACCEL_DIVISOR)
            deltaT = max(MIN_DELTAT, deltaT)
            deltaT = min(MAX_DELTAT_LIVE, deltaT)
            deltaT = 1.0 / (60.0 * math.ceil((1.0 / 60.0) / deltaT)) # rounds deltaT to integer quotient of 1/60 e.g (1/60) / 10

            if use_mindeltat:
                deltaT = MIN_DELTAT

            time_elapsed += deltaT

            for i in range(np.shape(bodyData)[0]):
                # velocity update using accel
                bodyData[i][2] += bodyData[i][5] * deltaT
                bodyData[i][3] += bodyData[i][6] * deltaT

            for i in range(np.shape(bodyData)[0]):
                # position update using vel
                bodyData[i][0] += bodyData[i][2] * deltaT
                bodyData[i][1] += bodyData[i][3] * deltaT


    @classmethod
    def liveMotion(cls):
        # create data to be used by numba
        bodyData = np.empty((len(cls.bodies), 7))  # format is [body][xpos, ypos, xvel, yvel, mass, accel_x, accel_y]

        for i in range(len(cls.bodies)):
            body = cls.bodies[i]
            bodyData[i] = np.array([body.pos[0], body.pos[1], body.vel[0], body.vel[1], body.mass, 0, 0])

        cls.numbaLiveMotion(bodyData)

        for i in range(len(cls.bodies)):

            cls.bodies[i].pos = np.array([bodyData[i][0], bodyData[i][1]])
            cls.bodies[i].vel = np.array([bodyData[i][2], bodyData[i][3]])

            cls.bodies[i].trail.append(np.array([bodyData[i][0], bodyData[i][1]]))
            if (len(cls.bodies[i].trail)) > trailDuration * 60:
                cls.bodies[i].trail.popleft()


    @staticmethod
    @njit
    def numbaFutureTrails(bodyData, futureTrailData, cameraBodyFocus, cameraMode):

        futureTrailPos = 0
        focused_body_start_x = 0
        focused_body_start_y = 0
        if cameraBodyFocus:
            focused_body_start_x = bodyData[cameraMode][0]
            focused_body_start_y = bodyData[cameraMode][1]

        for update in range(futureTrailUpdates):

            use_mindeltat = False
            for i in range(np.shape(bodyData)[0]):
                # setting accel to 0
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
                    if r_mag < CLOSEST_DISTANCE:
                        use_mindeltat = True
                        continue
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

            max_accel_for_vel = 0
            for i in range(np.shape(bodyData)[0]):
                max_accel_for_vel = max(max_accel_for_vel, math.sqrt(bodyData[i][5]**2 + bodyData[i][6]**2) / math.sqrt(bodyData[i][2]**2 + bodyData[i][3]**2))
            deltaT = 1 / (max_accel_for_vel * DELTAT_ACCEL_DIVISOR)
            deltaT = max(MIN_DELTAT, deltaT)
            deltaT = min(MAX_DELTAT_FUTURE, deltaT)
            # deltaT = 1.0 / (60.0 * math.ceil((1.0 / 60.0) / deltaT)) # rounds deltaT to integer quotient of 1/60 e.g (1/60) / 10

            if use_mindeltat:
                deltaT = MIN_DELTAT

            for i in range(np.shape(bodyData)[0]):
                # velocity update using accel
                bodyData[i][2] += bodyData[i][5] * deltaT
                bodyData[i][3] += bodyData[i][6] * deltaT

            for i in range(np.shape(bodyData)[0]):
                # position update using vel
                bodyData[i][0] += bodyData[i][2] * deltaT
                bodyData[i][1] += bodyData[i][3] * deltaT

            if update % timeStepsPerTrailPoint == 0:
                focused_body_x = 0
                focused_body_y = 0
                if cameraBodyFocus:
                    focused_body_x = bodyData[cameraMode][0]
                    focused_body_y = bodyData[cameraMode][1]
                for bodyPos in range(np.shape(bodyData)[0]):
                    futureTrailData[bodyPos][futureTrailPos] = np.array([bodyData[bodyPos][0] - focused_body_x + focused_body_start_x, bodyData[bodyPos][1] - focused_body_y + focused_body_start_y])
                futureTrailPos += 1


    @classmethod
    def calculateFutureTrails(cls):
        # creating data to be used by numba
        bodyData = np.empty( (len(cls.bodies), 7) )  # format is [body][xpos, ypos, xvel, yvel, mass, accel_x, accel_y]
        futureTrailData = np.empty( (len(cls.bodies), int(futureTrailUpdates / timeStepsPerTrailPoint), 2) )  # format is [body][trailPoint][xpos, ypos]

        for i in range(len(cls.bodies)):
            body = cls.bodies[i]
            bodyData[i] = np.array([body.pos[0], body.pos[1], body.vel[0], body.vel[1], body.mass, 0, 0])

        cls.numbaFutureTrails(bodyData, futureTrailData, cameraBodyFocus, cameraMode)

        for i in range(len(cls.bodies)):
            cls.bodies[i].futureTrail = deque(futureTrailData[i])


    # VISUALS

    def render(self, surface):
        currentPos = self.pos
        pygame.draw.circle(surface, self.color, toScreenCoords(currentPos), max(3, self.radius * zoom))

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



    @classmethod
    def getEnergy(cls):
        energy = 0
        for i in range(len(cls.bodies)):
            body1 = cls.bodies[i]
            energy += 0.5 * body1.mass * (body1.vel[0]**2 + body1.vel[1]**2)
            for j in range(i+1,len(cls.bodies)):
                body2 = cls.bodies[j]
                energy += -G * body1.mass * body2.mass / math.sqrt((body2.pos[0] - body1.pos[0])**2 + (body2.pos[1] - body1.pos[1])**2)
        return energy