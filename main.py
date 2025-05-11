# main.py

import pygame
import os # os is used by settings.py, but good to have here if any direct path ops were needed later

# Import all constants and settings
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SKY_BLUE, BLACK, WHITE,
                      SPRITESHEET_FILENAME, PLAYER_ANIMATION_TICKS_PER_FRAME, GREEN)


# Import the classes from their respective files
from spritesheet import Spritesheet
from player import Player
from platform import Platform

# --- Pygame Initialization ---
try:
    pygame.init()
except Exception as e:
    print(f"Error initializing Pygame: {e}")
    exit()

# --- Screen Setup ---
# The pygame.DOUBLEBUF flag is now set here directly
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Sorcery Game - Refactored")
except pygame.error as e:
    print(f"Error setting up the screen: {e}")
    pygame.quit()
    exit()

clock = pygame.time.Clock()

# --- Game Assets and Setup ---

# Animation data for the wizard (can be moved to a data file or player_settings later if complex)
wizard_animations_data = {
    "walk_left":  { "x": 0,   "y": 75, "w": 24, "h": 24, "count": 4, "spacing": 1},
    "idle_front": { "x": 100, "y": 75, "w": 24, "h": 24, "count": 4, "spacing": 1},
    "walk_right": { "x": 200, "y": 75, "w": 24, "h": 24, "count": 4, "spacing": 1}
}
if not wizard_animations_data: # Should not happen with hardcoded data
    print("Warning: wizard_animations_data is empty before Player creation.")

# Load Spritesheet
try:
    my_spritesheet = Spritesheet(SPRITESHEET_FILENAME)
except SystemExit: # Spritesheet class raises SystemExit on load failure
    print("Aborting: Failed to initialize Spritesheet in main.py.")
    pygame.quit()
    exit()
except Exception as e: # Catch any other unexpected errors
    print(f"Unexpected error loading spritesheet: {e}")
    pygame.quit()
    exit()

# Create Sprite Groups
all_sprites = pygame.sprite.Group() # Group for ALL sprites (for updating and drawing)
platforms = pygame.sprite.Group()   # Group specifically for platforms (for collision)    


# Create Player Instance
player_start_pos = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)
try:
    # Player will use PLAYER_ANIMATION_TICKS_PER_FRAME from settings by default,
    # but we can override it here or change it at runtime.
    # Let's use the one from settings to ensure it matches what was found best.
    initial_anim_ticks = PLAYER_ANIMATION_TICKS_PER_FRAME
    
    wizard = Player(my_spritesheet, wizard_animations_data,
                    initial_animation="idle_front",
                    position=player_start_pos,
                    animation_ticks_per_frame=initial_anim_ticks) # Use constant from settings initially
    
    if not wizard.animations: # Check after creation
        print("CRITICAL: Player object created, but its animations dictionary is empty. Check spritesheet loading and animation data.")
        # Decide if you want to exit or try to continue with a placeholder
        # For now, let's assume if this happens, it's critical.
        raise ValueError("Player animations not loaded.")

    all_sprites = pygame.sprite.Group()
    all_sprites.add(wizard)

except ValueError as ve: # Catch specific error from above
    print(ve)
    pygame.quit()
    exit()
except Exception as e:
    print(f"Error creating Player instance or sprite group: {e}")
    pygame.quit()
    exit()


# --- Create Platforms ---
# Define some platforms (x, y, width, height)
# Ground platform
platform1 = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40) # Using default BLACK color
# Floating platform
platform2 = Platform(SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT - 150, 200, 20)
# Another floating platform
platform3 = Platform(100, SCREEN_HEIGHT - 250, 150, 20, (100, 100, 100)) # Grey color

# Add platforms to the sprite groups
platforms.add(platform1)
platforms.add(platform2)
platforms.add(platform3)

all_sprites.add(platform1) # Add to all_sprites for drawing
all_sprites.add(platform2)
all_sprites.add(platform3)

# --- Game Loop ---
running = True
frame_count = 0 # For dt spike check, can be removed if confident dt is stable
while running:
    dt = clock.tick(FPS) / 1000.0 # Delta time in seconds
    frame_count += 1

    # Optional DT Spike Check
    # expected_dt = 1.0 / FPS
    # if frame_count > FPS * 2 and dt > expected_dt * 1.5:
    #     print(f"High dt spike: {dt*1000:.2f}ms (Expected: {expected_dt*1000:.2f}ms) at game time {pygame.time.get_ticks()}ms")

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Runtime switching of animation speed for testing
            if event.key == pygame.K_1:
                wizard.animation_ticks_per_frame = 7
                print(f"Animation speed: {wizard.animation_ticks_per_frame} ticks per frame")
            if event.key == pygame.K_2:
                wizard.animation_ticks_per_frame = 8
                print(f"Animation speed: {wizard.animation_ticks_per_frame} ticks per frame")
            if event.key == pygame.K_3:
                wizard.animation_ticks_per_frame = 6 # A bit faster
                print(f"Animation speed: {wizard.animation_ticks_per_frame} ticks per frame")
            if event.key == pygame.K_ESCAPE: # Added an escape key to quit
                running = False
    
    # Update Game State
    # Ensure all_sprites and wizard were successfully initialized
    if 'all_sprites' in locals() and 'wizard' in locals() and wizard is not None:
        all_sprites.update(dt) # dt is passed to player.update -> player.handle_input_and_movement
    else:
        # This should ideally not be reached due to earlier exit() calls on error
        print("Error: all_sprites or wizard not initialized for update.")
        running = False # Stop the game if essential objects are missing

    # Draw / Render
    screen.fill(BLACK)
    if 'all_sprites' in locals() and 'wizard' in locals() and wizard is not None:
        all_sprites.draw(screen)
    else:
        # Fallback rendering if player/group somehow missing and game didn't exit
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Error: Player or sprite group missing.", True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(text_surface, text_rect)
        
    pygame.display.flip()

# --- Cleanup ---
pygame.quit()
print("Game exited cleanly.")