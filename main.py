import gravitationalbody

from gravitationalbody import GravitationalBody

import pygame, time
import numpy as np
from numpy import float64


# Create player

ship = GravitationalBody((20000, 0),  (0, 800), 0.01, 5, "red")


# Create gravitational bodies

GravitationalBody((0, 0), (0, 0.01), 300000, 2000)
GravitationalBody((0, 20000), (-1200, 0), 1000, 200)
GravitationalBody((0, 21000), (-1500, 0), 20, 20)
bodies = GravitationalBody.bodies


# Physics variables

gamePaused = False
timeAcceleration = 1

shipVelBeforeManeuver = 0


# Screen variables

screenWidth = gravitationalbody.screenWidth = 1200
screenHeight = gravitationalbody.screenHeight = 720
fps = 60


# Display variables

cameraMode = 1
cameraUnlocked = False
trackingOffset = False
cameraBodyFocus = False

cameraPos = np.array([0,0])
cameraOffset = np.array([0,0], dtype=float64)

zoom = 0.01

zoomRate = 1

showFutureTrails = False


# Colors

space_color = (20, 20, 23)


# User Input Variables
prograde_thrust = 0
prograde_increase_rate = 0.01
radial_thrust = 0
radial_increase_rate = 0.01


# User Input Functions

def maneuver_ship(prograde, radial):
    if not cameraBodyFocus:
        prograde_unit = shipVelBeforeManeuver / np.linalg.norm(shipVelBeforeManeuver)
        radial_unit =  np.array([-shipVelBeforeManeuver[1], shipVelBeforeManeuver[0]]) / np.linalg.norm(shipVelBeforeManeuver)
    else:
        prograde_unit = shipVelBeforeManeuver - bodies[cameraMode].vel
        prograde_unit /= np.linalg.norm(prograde_unit)
        radial_unit = bodies[cameraMode].pos - ship.pos
        radial_unit /= np.linalg.norm(radial_unit)

    if prograde != 0:
        ship.vel += prograde * prograde_unit
    elif radial != 0:
        ship.vel += radial * radial_unit


# Prior to Loading Display

gravitationalbody.TOTAL_ENERGY = GravitationalBody.getEnergy()

# cameraBodyFocus = True
# gravitationalbody.updateCamera(cameraPos, zoom, cameraMode, cameraBodyFocus)
# GravitationalBody.calculateFutureTrails()
# array = np.array("hello", 2, 3)


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
                cameraMode = (cameraMode + 1) % len(bodies)
                cameraOffset = np.array([0,0], dtype=float64)
                cameraUnlocked = False
            if event.key == pygame.K_LEFT:
                cameraMode = (cameraMode - 1) % len(bodies)
                cameraOffset = np.array([0, 0], dtype=float64)
                cameraUnlocked = False
            if event.key == pygame.K_UP:
                zoomRate = 1.03
            if event.key == pygame.K_DOWN:
                zoomRate = 0.97
            if event.key == pygame.K_SPACE:
                shipVelBeforeManeuver = np.copy(ship.vel)
                gamePaused = not gamePaused
            if event.key == pygame.K_PERIOD:
                timeAcceleration *= 2
            if event.key == pygame.K_COMMA:
                timeAcceleration = max(1, int(timeAcceleration/2))
            if event.key == pygame.K_LSHIFT:
                showFutureTrails = not showFutureTrails
            if event.key == pygame.K_RSHIFT:
                cameraUnlocked = not cameraUnlocked
                cameraOffset = 0
            if event.key == pygame.K_SLASH:
                cameraBodyFocus = not cameraBodyFocus

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

        if event.type == pygame.MOUSEBUTTONDOWN:
            trackingOffset = True
            pygame.mouse.get_rel()

        if event.type == pygame.MOUSEBUTTONUP:
            trackingOffset = False


    # Maneuvers

    if prograde_thrust != 0 or radial_thrust != 0: maneuver_ship(prograde_thrust, radial_thrust)


    # Physics Updates

    if not gamePaused:
        for _ in range(timeAcceleration):
            GravitationalBody.liveMotion()

    if showFutureTrails:
        GravitationalBody.calculateFutureTrails()


    # Camera Updates

    zoom *= zoomRate

    if not cameraUnlocked:
        cameraPos = np.copy(bodies[cameraMode].pos) + cameraOffset
    else:
        cameraPos += cameraOffset
        cameraOffset = 0

    if trackingOffset:
        mouseMovement = pygame.mouse.get_rel()
        cameraOffset += np.array([float(-mouseMovement[0]) / zoom, float(mouseMovement[1]) / zoom], dtype=float64)

    gravitationalbody.updateCamera(cameraPos, zoom, cameraMode, cameraBodyFocus)


    # Rendering all visuals

    screen.fill(space_color)  # filling screen with color to wipe away previous frame

    if showFutureTrails:
        start2 = time.time()
        GravitationalBody.renderFutureTrails(screen)
        # print("future trail time: ", 0.016 / (time.time() - start2))
    GravitationalBody.renderTrails(screen)
    GravitationalBody.renderBodies(screen)

    pygame.display.flip()  # flip() the display to put new visuals on screen

    print("total frame time", 0.016 / (time.time() - start))
    clock.tick(fps)  # update game clock

pygame.quit()

print(timeAcceleration)