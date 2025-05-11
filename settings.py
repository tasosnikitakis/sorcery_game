# settings.py

import os
import pygame # Needed for things like FPS constant in calculations if desired, and color constants

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60 # Frames per second

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)


#Asset paths
# your_project_root/
# |-- assets/
#     |-- images/
#         |-- Amstrad CPC - Sorcery - Characters.png
SPRITESHEET_BASENAME = "Amstrad CPC - Sorcery - Characters.png"
SPRITESHEET_FILENAME = os.path.join("assets", "images", SPRITESHEET_BASENAME)

# Player Settings
PLAYER_SCALE_FACTOR = 3
PLAYER_ANIMATION_TICKS_PER_FRAME = 7
# Threshold for velocity (pixels per second) to be considered moving for animation state changes
PLAYER_ANIMATION_VELOCITY_THRESHOLD = 5.0


# Player movement speeds
# Define base speeds in a way that's easy to understand (e.g., conceptual pixels per game tick if tied to FPS)
# Or directly as pixels per second. Let's use the pixels-per-second approach directly here
# based on the previous values (6 pixels/frame * 60 FPS = 360 pps)
PLAYER_SPEED_PPS = 360  # Pixels per second for horizontal and UP/DOWN key movement
PLAYER_GRAVITY_PPS = 300 # Pixels per second for gravity pull when idle or not moving up

