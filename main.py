import gravitationalbody
from gravitationalbody import *
import pygame


# Create gravitational bodies

bodies = GravitationalBody.bodies
GravitationalBody(0, 0, 0, 0, 5, 20)
GravitationalBody(-100, 0, 0, 50, 1)


# Create player

player = GravitationalBody(100, 0, 0, -50, 1)


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


    # Physics Updates / Game Updates

    GravitationalBody.calculateMotion(fps, subUpdates)


    # Rendering all visuals

    screen.fill("black")  # filling screen with color to wipe away previous frame

    GravitationalBody.renderAll(screen, 1, 0, 0)


    pygame.display.flip()  # flip() the display to put new visuals on screen



    clock.tick(fps)  # update game clock

pygame.quit()