# Gravity-Game
Control a spaceship to get to where you need to be! This is my first game, made using pygame and to improve my skills.

## Current Status: In progress
Not currently near minimum viable product

## Goals
- Use OOP
- Create basic 2d graphics using sprites
- Decently good looking art style
- Good user controls
- Mildly fun concept
- Sound effects?
- Some procedurally generated levels

## Next Steps
2. URGENT: rewrite gravity simulation code for SPEED and simplicity
   3. use numpy/numba
   4. must be able to calculate entire future trail in one frame
4. Use pygame.draw.aalines instead of Surface.set_at to draw trail (>5x faster) 
6. Add buttons for better UX
3. Add realtime maneuvers where key is held instead of pressing a key for large jarring increments
2. Add sprites and make it good looking
3. Finalize

## Potential Changes
- Maybe make trail its own class/object
- Look up best practices for sharing variables across modules and implement this!!!