# Star Collector

A beginner-friendly 2D game built with Python and Pygame. Move a little ship around the screen, collect stars for points, and avoid bouncing enemies. The project focuses on clean, well-commented code that is easy for newcomers to read and modify.

## Game Concept
- **Objective:** Collect as many stars as possible.
- **Lives:** You start with 3 lives. Colliding with an enemy costs 1 life.
- **Difficulty:** Every 5 points increases difficulty by adding faster enemies.
- **End:** The game ends when your lives reach 0.

## Controls
- **Movement:** Arrow keys or WASD
- **Start:** Enter (from the menu)
- **Pause/Resume:** P
- **Restart:** R (on the Game Over screen)
- **Quit:** ESC (on the Game Over screen) or close the window

## How to Run
1. Install Python 3.10+.
2. Install Pygame: `pip install pygame`.
3. Run the game: `python main.py`.
4. (Optional) Add custom images or sounds to the `assets/` folder:
   - `player.png`, `star.png`, `enemy.png` for sprites
   - `collect.wav`, `hit.wav` for sound effects
   The game will gracefully fall back to colored shapes if files are missing.

## Features and Classes
- **Player** – Handles movement, drawing, and collision box clamping to the window.
- **Star** – Spawns at random positions; when collected, increases score and respawns.
- **Enemy** – Moves with simple bouncing AI; speeds up with difficulty.
- **Game** – Manages states (MENU/RUNNING/PAUSED/GAME_OVER), scoring, lives, difficulty, and rendering.
- **Delta time & fixed FPS** – Smooth movement at 60 FPS.
- **UI overlays** – Score and lives displayed on screen.
- **Graceful fallbacks** – Runs with or without external assets; handles missing sounds safely.
- **Helpful console output** – Prints tips when starting or restarting the game.

## Extra Beginner-Friendly Touches
- Clear comments throughout `main.py` explaining what each part does.
- Simple shapes for visuals by default—no asset downloads required.
- Invulnerability cooldown after taking damage to prevent instant double hits.
- Organized constants and helper functions to make tweaking the game easy.

Enjoy collecting stars and dodging enemies!
