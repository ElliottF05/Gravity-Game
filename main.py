import gravitationalbody

from gravitationalbody import GravitationalBody

import pygame, time
import numpy as np
from collections import deque


# Create player

ship = GravitationalBody((0, 0),  (0, 0.0001), 1, 5, "red")


# Create gravitational bodies

GravitationalBody((-200, 0), (0, 70), 50, 20)
GravitationalBody((200, 0), (0, -70), 50, 20)
bodies = GravitationalBody.bodies


# Physics variables

subUpdates = gravitationalbody.subUpdates = 10
gamePaused = False
timeAcceleration = 1

shipVelBeforeManeuver = 0


# Screen variables

screenWidth = gravitationalbody.screenWidth = 1200
screenHeight = gravitationalbody.screenHeight = 720
fps = gravitationalbody.fps = 60


# Display variables

gravitationalbody.trailDuration = 1
gravitationalbody.futureTrailUpdates = 3000
gravitationalbody.futureTrailUpdatesPerFrame = 1
gravitationalbody.timeStepsPerTrailPoint = 10

cameraModeList = deque(["zero", "ship", "centerOfMass"])
cameraMode = deque[0]

cameraPos = np.array([0,0])
zoom = 1

zoomRate = 1


# Colors

space_color = (20, 20, 23)


# User Input Variables
prograde_thrust = 0
prograde_increase_rate = 0.01
radial_thrust = 0
radial_increase_rate = 0.01


# User Input Functions

def maneuver_ship(prograde, radial):
    if prograde != 0:
        ship.vel += prograde * shipVelBeforeManeuver / np.linalg.norm(shipVelBeforeManeuver)
    elif radial != 0:
        ship.vel += radial * np.array([-shipVelBeforeManeuver[1], shipVelBeforeManeuver[0]]) / np.linalg.norm(shipVelBeforeManeuver)

    GravitationalBody.calculateFutureTrails()


# Prior to Loading Display



# Pygame setup

pygame.init()
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption("Gravity Game")

clock = pygame.time.Clock()
running = True



# Running Loop

while running:
    start = time.time()

    # User input

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                cameraModeList.rotate(-1)
                cameraMode = cameraModeList[0]
            if event.key == pygame.K_LEFT:
                cameraModeList.rotate(1)
                cameraMode = cameraModeList[0]
            if event.key == pygame.K_UP:
                zoomRate = 1.03
            if event.key == pygame.K_DOWN:
                zoomRate = 0.97
            if event.key == pygame.K_SPACE:
                shipVelBeforeManeuver = np.copy(ship.vel)
                GravitationalBody.calculateFutureTrails()
                gamePaused = not gamePaused
            if event.key == pygame.K_PERIOD:
                timeAcceleration += 1
            if event.key == pygame.K_COMMA:
                timeAcceleration = max(1, timeAcceleration-1)

            if gamePaused:
                if event.key == pygame.K_w:
                    prograde_thrust = prograde_increase_rate
                if event.key == pygame.K_s:
                    prograde_thrust = -prograde_increase_rate
                if event.key == pygame.K_a:
                    radial_thrust = radial_increase_rate
                if event.key == pygame.K_d:
                    radial_thrust = -radial_increase_rate
                if event.key == pygame.K_e:
                    prograde_increase_rate *= 2
                    radial_increase_rate *= 2
                if event.key == pygame.K_q:
                    prograde_increase_rate *= 0.5
                    radial_increase_rate *= 0.5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                zoomRate = 1

            if gamePaused:
                if event.key == pygame.K_w:
                    prograde_thrust = 0
                if event.key == pygame.K_s:
                    prograde_thrust = 0
                if event.key == pygame.K_a:
                    radial_thrust = 0
                if event.key == pygame.K_d:
                    radial_thrust = 0


    # Maneuvers

    if prograde_thrust != 0 or radial_thrust != 0: maneuver_ship(prograde_thrust, radial_thrust)


    # Physics Updates

    if not gamePaused:
        for _ in range(timeAcceleration):
            GravitationalBody.calculateMotion()


    # Camera Updates

    zoom *= zoomRate

    if cameraMode == "centerOfMass":
        cameraPos = GravitationalBody.getCenterOfMass()
    if cameraMode == "ship":
        cameraPos = ship.pos
    if cameraMode == "zero":
        cameraPos = np.array([0,0])

    gravitationalbody.updateCamera(cameraPos, zoom)


    # Rendering all visuals

    screen.fill(space_color)  # filling screen with color to wipe away previous frame

    if gamePaused:
        GravitationalBody.renderFutureTrails(screen)

    GravitationalBody.renderTrails(screen)
    GravitationalBody.renderBodies(screen)

    pygame.display.flip()  # flip() the display to put new visuals on screen

    # print(0.016 / (time.time() - start))
    clock.tick(fps)  # update game clock

pygame.quit()