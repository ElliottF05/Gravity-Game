import gravitationalbody
from gravitationalbody import *
import pygame

# Create gravitational bodies

bodies = GravitationalBody.bodies
GravitationalBody(0, 0, 0, 0, 5, 20)
GravitationalBody(-100, 0, 0, 50, 1)


# Create player

ship = GravitationalBody(100, 0, 0, -50, 1)


# Physics variables

subUpdates = 100

# Screen variables

screenWidth = 1200
screenHeight = 720
fps = 60

gravitationalbody.screenWidth = screenWidth
gravitationalbody.screenHeight = screenHeight


# Display variables

gravitationalbody.trailDuration = 1
gravitationalbody.trailUpdatePerFrame = 10

cameraModeList = deque(["ship", "centerOfMass", "showAll"])
cameraMode = deque[0]

cameraX = 0
cameraY = 0
zoom = 1



# Colors

space_color = (20, 20, 23)


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
                print(cameraMode)
            if event.key == pygame.K_LEFT:
                cameraModeList.rotate(1)
                cameraMode = cameraModeList[0]



    # Physics Updates / Game Updates

    GravitationalBody.calculateMotion(fps, subUpdates)

    if (cameraMode == "centerOfMass"):
        cameraX, cameraY = GravitationalBody.getCenterOfMass()
    if (cameraMode == "ship"):
        cameraX, cameraY = ship.xpos, ship.ypos
    if (cameraMode == "showAll"):
        cameraX, cameraY = GravitationalBody.getShowAllCameraPos()


    # Rendering all visuals

    screen.fill(space_color)  # filling screen with color to wipe away previous frame

    GravitationalBody.renderAll(screen, zoom, cameraX, cameraY)


    pygame.display.flip()  # flip() the display to put new visuals on screen



    clock.tick(fps)  # update game clock

pygame.quit()


# USER INPUT FUNCTIONS
