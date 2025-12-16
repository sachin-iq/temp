"""
Star Collector - A simple, beginner-friendly Pygame project.

This file contains everything you need to run the game:
- Game loop with menu, pause, and game-over states
- Classes for the Player, Star, Enemy, and Game manager
- Clear comments explaining what each part does

The game uses colored shapes by default and will gracefully fall back
if optional image or sound assets are missing.
"""

import os
import random
import sys
from pathlib import Path

import pygame

# -----------------------------
# Basic configuration constants
# -----------------------------
WIDTH, HEIGHT = 800, 600  # Window size
FPS = 60  # Fixed frames per second target
PLAYER_SPEED = 260  # Pixels per second
ENEMY_BASE_SPEED = 140  # Starting enemy speed
PLAYER_LIVES = 3

# Colors used in the game (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND = (20, 24, 30)
YELLOW = (255, 219, 88)
RED = (220, 80, 80)
BLUE = (90, 180, 255)
GREY = (180, 180, 180)

# Path helpers for optional assets
ASSETS_DIR = Path(__file__).parent / "assets"


# -----------------------------
# Helper functions
# -----------------------------
def safe_load_image(filename: str, size: tuple[int, int] | None = None) -> pygame.Surface | None:
    """Try to load an image from the assets folder.

    If loading fails, return None so the caller can use a fallback.
    """

    try:
        image_path = ASSETS_DIR / filename
        if not image_path.exists():
            return None
        image = pygame.image.load(image_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except Exception:
        # Any error (missing file, bad format) returns None.
        return None


def safe_load_sound(filename: str) -> pygame.mixer.Sound | None:
    """Try to load a sound effect from the assets folder.

    If the sound cannot be loaded, return None.
    """

    try:
        sound_path = ASSETS_DIR / filename
        if not sound_path.exists():
            return None
        return pygame.mixer.Sound(sound_path)
    except Exception:
        return None


def draw_text(surface: pygame.Surface, text: str, size: int, color: tuple[int, int, int], center: tuple[int, int]):
    """Render text to the screen at a position."""

    font = pygame.font.Font(None, size)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)


# -----------------------------
# Game object classes
# -----------------------------
class Player:
    """Represents the player character controlled by the user."""

    def __init__(self, start_pos: tuple[int, int]):
        self.speed = PLAYER_SPEED
        self.size = (40, 40)
        self.image = safe_load_image("player.png", self.size)
        self.color = BLUE
        self.rect = pygame.Rect(0, 0, *self.size)
        self.rect.center = start_pos

    def handle_input(self, keys: pygame.key.ScancodeWrapper, dt: float):
        """Move the player according to keyboard input and delta time."""

        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # Normalize diagonal movement to keep speed consistent.
        if dx and dy:
            dx *= 0.7071  # 1/sqrt(2)
            dy *= 0.7071

        self.rect.x += int(dx * self.speed * dt)
        self.rect.y += int(dy * self.speed * dt)

        # Keep the player inside the window.
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self, surface: pygame.Surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=6)


class Star:
    """Collectible item that increases the player's score."""

    def __init__(self):
        self.radius = 10
        self.color = YELLOW
        self.image = safe_load_image("star.png", (24, 24))
        self.rect = pygame.Rect(0, 0, 24, 24)
        self.respawn()

    def respawn(self):
        """Move the star to a new random location inside the window."""

        padding = 30
        x = random.randint(padding, WIDTH - padding)
        y = random.randint(padding, HEIGHT - padding)
        self.rect.center = (x, y)

    def draw(self, surface: pygame.Surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.circle(surface, self.color, self.rect.center, self.radius)


class Enemy:
    """Enemy that bounces around the screen."""

    def __init__(self, speed: float):
        self.size = (36, 36)
        self.color = RED
        self.image = safe_load_image("enemy.png", self.size)
        self.rect = pygame.Rect(0, 0, *self.size)
        padding = 50
        self.rect.center = (
            random.randint(padding, WIDTH - padding),
            random.randint(padding, HEIGHT - padding),
        )
        # Start with a random velocity direction.
        dx = random.choice([-1, 1])
        dy = random.choice([-1, 1])
        self.velocity = pygame.Vector2(dx, dy).normalize() * speed

    def update(self, dt: float):
        # Move based on velocity and delta time.
        self.rect.x += int(self.velocity.x * dt)
        self.rect.y += int(self.velocity.y * dt)

        # Bounce off the walls by reversing direction when hitting edges.
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.velocity.x *= -1
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.velocity.y *= -1
            self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self, surface: pygame.Surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=4)


class Game:
    """Main game manager that controls state, scoring, and drawing."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.state = "MENU"  # Other states: RUNNING, PAUSED, GAME_OVER
        self.clock = pygame.time.Clock()
        self.player = Player((WIDTH // 2, HEIGHT // 2))
        self.star = Star()
        self.enemies: list[Enemy] = []
        self.score = 0
        self.lives = PLAYER_LIVES
        self.difficulty_level = 1
        self.damage_cooldown = 0.0  # Invulnerability timer in seconds

        # Optional sounds
        self.collect_sound = safe_load_sound("collect.wav")
        self.hit_sound = safe_load_sound("hit.wav")

        # Prepare UI font once for efficiency.
        self.ui_font = pygame.font.Font(None, 32)

    def start_game(self):
        """Reset game variables for a fresh run."""

        print("Starting a new game of Star Collector...")
        self.state = "RUNNING"
        self.score = 0
        self.lives = PLAYER_LIVES
        self.difficulty_level = 1
        self.damage_cooldown = 0
        self.player = Player((WIDTH // 2, HEIGHT // 2))
        self.star = Star()
        self.enemies = [Enemy(ENEMY_BASE_SPEED)]

    def restart(self):
        """Restart after game over."""

        print("Restarting Star Collector. Good luck!")
        self.start_game()

    def update_difficulty(self):
        """Increase difficulty every 5 points by adding enemies or speed."""

        new_level = self.score // 5 + 1
        if new_level > self.difficulty_level:
            self.difficulty_level = new_level
            # Alternate between adding an enemy and speeding up existing ones.
            if len(self.enemies) < 5:
                self.enemies.append(Enemy(ENEMY_BASE_SPEED + 20 * self.difficulty_level))
            else:
                for enemy in self.enemies:
                    enemy.velocity *= 1.1

    def handle_events(self) -> bool:
        """Process input events. Returns False when quitting."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU" and event.key == pygame.K_RETURN:
                    self.start_game()
                elif self.state == "RUNNING" and event.key == pygame.K_p:
                    self.state = "PAUSED"
                elif self.state == "PAUSED" and event.key == pygame.K_p:
                    self.state = "RUNNING"
                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_r:
                        self.restart()
                    elif event.key == pygame.K_ESCAPE:
                        return False
        return True

    def update(self, dt: float):
        """Update game logic depending on the current state."""

        if self.state != "RUNNING":
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, dt)
        self.star_collision()

        for enemy in self.enemies:
            enemy.update(dt)

        # Damage cooldown prevents rapid consecutive hits.
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        self.check_enemy_collisions()

    def star_collision(self):
        """Check if the player collected the star."""

        if self.player.rect.colliderect(self.star.rect):
            self.score += 1
            self.star.respawn()
            self.update_difficulty()
            if self.collect_sound:
                self.collect_sound.play()

    def check_enemy_collisions(self):
        """Handle collisions between the player and enemies."""

        if self.damage_cooldown > 0:
            return

        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.lives -= 1
                self.damage_cooldown = 1.0  # 1 second of invulnerability
                if self.hit_sound:
                    self.hit_sound.play()
                # Reposition player to the center for a fair restart after hit.
                self.player.rect.center = (WIDTH // 2, HEIGHT // 2)
                if self.lives <= 0:
                    self.state = "GAME_OVER"
                break

    def draw_ui(self):
        """Draw score and lives at the top-left corner."""

        score_text = self.ui_font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.ui_font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_text, (15, 10))
        self.screen.blit(lives_text, (15, 40))

    def draw(self):
        """Render everything based on the current state."""

        self.screen.fill(BACKGROUND)

        if self.state == "MENU":
            draw_text(self.screen, "Star Collector", 56, YELLOW, (WIDTH // 2, HEIGHT // 3))
            draw_text(self.screen, "Press ENTER to Start", 32, GREY, (WIDTH // 2, HEIGHT // 2))
            draw_text(self.screen, "Move with Arrow Keys or WASD", 24, WHITE, (WIDTH // 2, HEIGHT // 2 + 60))
            draw_text(self.screen, "Press P to Pause during the game", 24, WHITE, (WIDTH // 2, HEIGHT // 2 + 90))
        elif self.state == "RUNNING":
            self.star.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            self.player.draw(self.screen)
            self.draw_ui()
        elif self.state == "PAUSED":
            self.star.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            self.player.draw(self.screen)
            self.draw_ui()
            draw_text(self.screen, "Paused", 48, GREY, (WIDTH // 2, HEIGHT // 2))
            draw_text(self.screen, "Press P to Resume", 28, WHITE, (WIDTH // 2, HEIGHT // 2 + 50))
        elif self.state == "GAME_OVER":
            draw_text(self.screen, "Game Over", 56, RED, (WIDTH // 2, HEIGHT // 3))
            draw_text(self.screen, f"Final Score: {self.score}", 36, WHITE, (WIDTH // 2, HEIGHT // 2))
            draw_text(self.screen, "Press R to Restart", 28, GREY, (WIDTH // 2, HEIGHT // 2 + 50))
            draw_text(self.screen, "Press ESC to Quit", 28, GREY, (WIDTH // 2, HEIGHT // 2 + 90))

        pygame.display.flip()

    def run(self):
        """Main loop. Returns when the user quits."""

        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds
            running = self.handle_events()
            self.update(dt)
            self.draw()


def initialize_pygame():
    """Initialize pygame modules safely."""

    pygame.init()
    # Try to initialize the mixer for sounds; ignore failures so the game still runs.
    try:
        pygame.mixer.init()
    except Exception:
        print("Sound initialization failed. Continuing without audio.")


def main():
    initialize_pygame()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Star Collector")

    game = Game(screen)
    print("Welcome to Star Collector! Press ENTER on the menu to begin.")
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
