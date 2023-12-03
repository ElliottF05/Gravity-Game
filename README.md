# Gravity-Game
Control a spaceship (red) to get to wherever you want to be! While originally intended to be a game, this is more of an interactive physics demo.

## Usage
1. Run main.py in a **conda environment**
2. If desired, set initial body conditions at the top of main.py

## Controls

### Ship Maneuvers:
[W] [S] - prograde/retrograde burns (hold)  
[A] [D] - radial in/out burns (hold)  
[Q] [E] - increase/decrease rate of maneuvers (press)

### Camera Controls
[UP] [DOWN] - zoom in/out   
[LEFT] [RIGHT] - change which body camera is focused on  
[DRAG/PAN WITH MOUSE] - pan camera around  

### Display Controls
[LSHIFT] - show future paths of all object  
[/] - enable/disable paths being drawn relative to the body the camera is focused on (**USE THIS FOR MANUEVERS**)  
[SPACE] - pause simulation

## Current Status: In progress
At minimum viable product

## Personal Note / Next Steps
I'm currently very happy with how the physics of the game has turned out and how I've overcome the challenges I've faced.
This is also the part the interests me the most. That being said, I'm not as interested/passionate about adding sprites, sound effects, a nice UI, etc.
For now, I want to finalize some physics changes, and potentially revisit this later when I have a better understanding of sprites and graphics (so it's not so daunting requiring an entire new learning process).

That being said, here are my next steps:

1. Revisit at a later date after learning best practices for sprites. I also still want to look up best practices for using moduels and classes as I feel my way is convoluted.

## Goals
- Use OOP
- Create basic 2d graphics using sprites
- Decently good looking art style
- Good user controls
- Mildly fun concept
- Sound effects?
- Some procedurally generated levels


## Potential Changes
- Look up best practices for sharing variables across modules and implement this