import gravitationalbody, vectors

from gravitationalbody import GravitationalBody

import pygame
from collections import deque

# Create gravitational bodies

bodies = GravitationalBody.bodies
GravitationalBody((0, 0), (0, 0), 50, 20)
GravitationalBody((-300, 0), (0, 60), 0.1)


# Create player

ship = GravitationalBody((100, 0),  (0, -150), 0.1)


# Physics variables

subUpdates = 100
gamePaused = False

# Screen variables

screenWidth = 1200
screenHeight = 720
fps = 60

gravitationalbody.screenWidth = screenWidth
gravitationalbody.screenHeight = screenHeight


# Display variables

gravitationalbody.trailDuration = 1
futureTrailDuration = 1
gravitationalbody.futureTrailDuration = futureTrailDuration
gravitationalbody.trailUpdatesPerFrame = 10

cameraModeList = deque(["ship", "centerOfMass"])
cameraMode = deque[0]

cameraX = 0
cameraY = 0
zoom = 1

zoomRate = 1


# Colors

space_color = (20, 20, 23)


# Prior to Loading Display

for i in range(60 * futureTrailDuration):
    GravitationalBody.calculateMotion(fps, subUpdates)


# Pygame setup

pygame.init()
screen = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption("Gravity Game")

font = pygame.font.Font("freesansbold.ttf", 16)
text = font.render("hello", True, "white", "black")

clock = pygame.time.Clock()
running = True


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
                gamePaused = not gamePaused

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                zoomRate = 1



    # Physics Updates
    if not gamePaused:
        GravitationalBody.calculateMotion(fps, subUpdates)


    # Camera Updates

    zoom *= zoomRate

    if (cameraMode == "centerOfMass"):
        cameraX, cameraY = GravitationalBody.getCenterOfMass()
    if (cameraMode == "ship"):
        cameraX, cameraY = ship.futureTrail[0][0], ship.futureTrail[0][1]

    gravitationalbody.updateCamera(cameraX, cameraY, zoom)


    # Rendering all visuals

    screen.fill(space_color)  # filling screen with color to wipe away previous frame

    if gamePaused:
        GravitationalBody.renderFutureTrails(screen)

    GravitationalBody.renderTrails(screen)
    GravitationalBody.renderBodies(screen)


    pygame.display.flip()  # flip() the display to put new visuals on screen



    clock.tick(fps)  # update game clock

pygame.quit()



# USER INPUT FUNCTIONS

