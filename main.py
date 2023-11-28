import gravitationalbody

from gravitationalbody import GravitationalBody

import pygame, time
import numpy as np
from collections import deque


# Create player

ship = GravitationalBody((100, 0),  (0, -150), 0.1)


# Create gravitational bodies

GravitationalBody((0, 0), (0, 0), 50, 20)
GravitationalBody((-300, 0), (0, 60), 0.1)
bodies = GravitationalBody.bodies


# Physics variables

subUpdates = gravitationalbody.subUpdates = 10
gamePaused = False


# Screen variables

screenWidth = gravitationalbody.screenWidth = 1200
screenHeight = gravitationalbody.screenHeight = 720
fps = gravitationalbody.fps = 60


# Display variables

gravitationalbody.trailDuration = 1
gravitationalbody.futureTrailDuration = futureTrailDuration = 8
gravitationalbody.trailUpdatesPerFrame = 5
gravitationalbody.futureTrailUpdatesPerFrame = 2

cameraModeList = deque(["ship", "centerOfMass"])
cameraMode = deque[0]

cameraPos = np.array([0,0])
zoom = 1

zoomRate = 1


# Colors

space_color = (20, 20, 23)


# User Input Variables
prograde_increment = 1
radial_increment = 1
currentVelUnitVector = None
currentNetGravVector = None

# User Input Functions

def maneuverShip(prograde, radial):

    if prograde != 0:
        ship.vel += prograde * ship.vel / np.linalg.norm(ship.vel)
    elif radial != 0:
        ship.vel += radial * np.array([-ship.vel[1], ship.vel[0]]) / np.linalg.norm(ship.vel)

    start = time.time()
    GravitationalBody.calculateFutureTrails()
    print(time.time() - start)


# Prior to Loading Display



# Pygame setup

pygame.init()
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption("Gravity Game")

clock = pygame.time.Clock()
running = True

# Text
font = pygame.font.Font("freesansbold.ttf", 16)
text = font.render("hello", True, "white", "black")


queue = deque()
queue.append(np.array([0,0]))
queue.append(np.array([1,0]))
queue.append(np.array([2,0]))

pygame.draw.aalines(screen, "white", True, queue)




# Running Loop

while running:


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
                zoomRate = 1.01
            if event.key == pygame.K_DOWN:
                zoomRate = 0.99
            if event.key == pygame.K_SPACE:
                GravitationalBody.calculateFutureTrails()
                gamePaused = not gamePaused

            if gamePaused:
                if event.key == pygame.K_w:
                    maneuverShip(prograde_increment,0)
                if event.key == pygame.K_s:
                    maneuverShip(-prograde_increment, 0)
                if event.key == pygame.K_a:
                    maneuverShip(0, radial_increment)
                if event.key == pygame.K_d:
                    maneuverShip(0, -radial_increment)
                if event.key == pygame.K_e:
                    prograde_increment *= 2
                    radial_increment *= 2
                if event.key == pygame.K_q:
                    prograde_increment *= 0.5
                    radial_increment *= 0.5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                zoomRate = 1



    # Physics Updates
    if not gamePaused:
        GravitationalBody.calculateMotion()



    # Camera Updates

    zoom *= zoomRate

    if (cameraMode == "centerOfMass"):
        cameraPos = GravitationalBody.getCenterOfMass()
    if (cameraMode == "ship"):
        cameraPos = ship.pos

    gravitationalbody.updateCamera(cameraPos, zoom)


    # Rendering all visuals

    screen.fill(space_color)  # filling screen with color to wipe away previous frame

    if gamePaused:
        start = time.time()
        GravitationalBody.renderFutureTrails(screen)
        # print(time.time() - start)

    GravitationalBody.renderTrails(screen)
    GravitationalBody.renderBodies(screen)

    screen.blit(text, (0,0))

    pygame.display.flip()  # flip() the display to put new visuals on screen



    clock.tick(fps)  # update game clock

pygame.quit()