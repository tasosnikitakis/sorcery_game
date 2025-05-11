# player.py

import pygame
# Import necessary constants from settings.py
from settings import (FPS, PLAYER_SCALE_FACTOR, PLAYER_ANIMATION_TICKS_PER_FRAME,
                      PLAYER_ANIMATION_VELOCITY_THRESHOLD, PLAYER_SPEED_PPS, PLAYER_GRAVITY_PPS,
                      SCREEN_WIDTH, SCREEN_HEIGHT) # SCREEN_WIDTH/HEIGHT needed for boundary checks

class Player(pygame.sprite.Sprite):
    """
    Represents the player character in the game.
    Handles player movement, animation, and state.
    """
    def __init__(self, spritesheet_obj, animation_frames_data, initial_animation, position=(100,100), 
                 # Use the constant from settings as the default
                 animation_ticks_per_frame=PLAYER_ANIMATION_TICKS_PER_FRAME):
        super().__init__()
        self.spritesheet = spritesheet_obj # Expects a Spritesheet object
        self.animations = {}
        self.scale_factor = PLAYER_SCALE_FACTOR # Use constant from settings
        self.load_animations(animation_frames_data)

        self.current_animation_name = None
        self.current_frames = []
        self.current_frame_index = 0
        
        self.animation_ticks_per_frame = animation_ticks_per_frame
        self.ticks_since_last_frame_change = 0

        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(0, 0)
        
        self.speed_pps = PLAYER_SPEED_PPS         # Use constant from settings
        self.gravity_pps = PLAYER_GRAVITY_PPS     # Use constant from settings

        self.facing_direction = "right" # Not currently used by animation logic, but good to have
        self.is_on_ground = False 

        self.image = None 
        self.rect = None
        # Initialize animation and ensure image/rect are created
        if initial_animation and self.animations.get(initial_animation):
            self.set_animation(initial_animation)
        else:
            # Fallback if initial_animation is invalid or animations are not loaded
            print(f"Warning: Initial animation '{initial_animation}' failed or was empty, or no animations loaded for Player.")
            # Create a placeholder image and rect
            self.image = pygame.Surface([32 * self.scale_factor, 32 * self.scale_factor], pygame.SRCALPHA)
            self.image.fill((255,0,0,128)) # Semi-transparent red
            self.rect = self.image.get_rect(topleft=position)
            if not self.animations:
                 print("CRITICAL: Player's animations dictionary is empty after init during fallback.")

    def load_animations(self, animation_frames_data):
        """
        Loads all animation sequences for the player from the spritesheet.
        Args:
            animation_frames_data (dict): A dictionary where keys are animation names
                                          and values are dicts with 'x', 'y', 'w', 'h',
                                          'count', and 'spacing' for the frames.
        """
        if not animation_frames_data:
            print("CRITICAL: animation_frames_data is empty in Player.load_animations.")
            return
        for name, data in animation_frames_data.items():
            frames = self.spritesheet.get_animation_frames(
                data["x"], data["y"], data["w"], data["h"],
                data["count"], data.get("spacing", 0),
                scale=self.scale_factor # Use player's scale factor
            )
            if not frames:
                print(f"Warning: No frames loaded for animation '{name}' in Player.load_animations.")
            self.animations[name] = frames
        if not self.animations:
             print("CRITICAL: Player's animations dictionary is still empty after loading attempts.")

    def set_animation(self, animation_name):
        """
        Sets the current animation for the player.
        Args:
            animation_name (str): The name of the animation to set.
        """
        if self.current_animation_name == animation_name and self.current_frames:
            return # Already playing this animation

        # print(f"[{pygame.time.get_ticks()}] Setting animation from '{self.current_animation_name}' to '{animation_name}' (Velocity: ({self.velocity.x:.2f}, {self.velocity.y:.2f}))")


        if not self.animations:
            print(f"CRITICAL: Attempting to set animation '{animation_name}', but self.animations is empty.")
            # Fallback image if animations are entirely missing
            self.image = pygame.Surface((32*self.scale_factor, 32*self.scale_factor), pygame.SRCALPHA); self.image.fill((0,255,255,128)) # Cyan placeholder
            if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
            else: self.rect.size = self.image.get_size()
            self.current_frames = []; self.current_animation_name = None # Ensure current_frames is empty list
            return

        if animation_name not in self.animations or not self.animations[animation_name]:
            print(f"Warning: Animation '{animation_name}' not found in self.animations or has no frames.")
            if self.current_frames and self.current_animation_name: return # Keep current valid animation
            
            # Attempt to set a fallback if no valid current animation
            for anim_key, anim_frames in self.animations.items():
                if anim_frames: # Found a valid animation
                    print(f"Fallback: Animation '{animation_name}' failed, setting to first available: '{anim_key}'")
                    self.current_animation_name = anim_key
                    self.current_frames = anim_frames
                    break 
            else: # No valid animations found at all
                print("CRITICAL: No valid animations available for fallback in set_animation.")
                self.image = pygame.Surface((32*self.scale_factor, 32*self.scale_factor), pygame.SRCALPHA); self.image.fill((255,255,0,128)) # Yellow
                if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
                else: self.rect.size = self.image.get_size()
                self.current_frames = []; self.current_animation_name = animation_name # Still note the intended name
                return

        self.current_animation_name = animation_name
        self.current_frames = self.animations[animation_name]
        self.current_frame_index = 0
        self.ticks_since_last_frame_change = 0 # Reset tick counter for new animation

        if not self.current_frames: # Should be caught by earlier checks, but as a final safeguard
            print(f"Warning: No frames assigned to self.current_frames for animation: {animation_name} after attempting to set it.")
            self.image = pygame.Surface((32*self.scale_factor, 32*self.scale_factor), pygame.SRCALPHA); self.image.fill((255,0,255,128)) # Magenta
            if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
            else: self.rect.size = self.image.get_size()
            return
            
        new_image = self.current_frames[self.current_frame_index]
        if self.rect is not None:
            current_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect(center=current_center)
        else: # Should only happen during initial __init__ if rect wasn't set yet
            self.image = new_image
            self.rect = self.image.get_rect(topleft=self.position)


    def handle_input_and_movement(self, dt):
        """
        Handles player input for movement and updates the player's position.
        Args:
            dt (float): Delta time, the time elapsed since the last frame in seconds.
        """
        keys = pygame.key.get_pressed()
        
        moving_left = keys[pygame.K_LEFT]
        moving_right = keys[pygame.K_RIGHT]
        
        target_horizontal_velocity = 0
        if moving_left and not moving_right:
            target_horizontal_velocity = -self.speed_pps
        elif moving_right and not moving_left:
            target_horizontal_velocity = self.speed_pps
        self.velocity.x = target_horizontal_velocity

        current_vy = self.gravity_pps
        if keys[pygame.K_UP]:
            current_vy = -self.speed_pps
        elif keys[pygame.K_DOWN]:
            current_vy = self.speed_pps
        self.velocity.y = current_vy
        
        self.position += self.velocity * dt
        
        # Ensure image and rect are valid before boundary checks, especially if init failed
        if self.image is None:
             if self.current_frames and self.current_frame_index < len(self.current_frames) and self.current_frames[self.current_frame_index]:
                  self.image = self.current_frames[self.current_frame_index]
             else: # Absolute fallback if no valid current animation frame
                  self.image = pygame.Surface((32 * self.scale_factor, 32 * self.scale_factor), pygame.SRCALPHA); self.image.fill((255,165,0,128)) # Orange placeholder
        
        if self.rect is None: # Initialize rect if it's None (e.g. if __init__ fallback occurred)
            if self.image: self.rect = self.image.get_rect(topleft=self.position)
            else: # Should not happen if image is created above
                 self.rect = pygame.Rect(self.position.x, self.position.y, 32*self.scale_factor, 32*self.scale_factor)

        self.rect.topleft = (round(self.position.x), round(self.position.y))

        # Boundary corrections: Adjust self.position then re-align rect to self.position
        corrected = False
        
        if self.rect.left < 0:
            self.position.x -= self.rect.left # self.rect.left is negative, so this adds to position.x
            corrected = True
        if self.rect.right > SCREEN_WIDTH:
            self.position.x -= (self.rect.right - SCREEN_WIDTH)
            corrected = True
        if self.rect.top < 0:
            self.position.y -= self.rect.top
            corrected = True
        if self.rect.bottom > SCREEN_HEIGHT:
            self.position.y -= (self.rect.bottom - SCREEN_HEIGHT) # Correct position
            self.is_on_ground = True
            self.velocity.y = 0 # Explicitly stop downward velocity upon "landing"
            corrected = True
        else:
            self.is_on_ground = False

        if corrected: # Re-align rect to the corrected self.position
            self.rect.topleft = (round(self.position.x), round(self.position.y))    


    def update_animation(self):
        """ Updates the current animation frame based on game ticks. """
        
        # Determine target animation based on velocity
        vel_x_direction = 0
        if self.velocity.x > PLAYER_ANIMATION_VELOCITY_THRESHOLD : vel_x_direction = 1
        elif self.velocity.x < -PLAYER_ANIMATION_VELOCITY_THRESHOLD: vel_x_direction = -1
        
        vel_y_direction = 0 # Not directly used for walk/idle choice if x is moving
        if self.velocity.y > PLAYER_ANIMATION_VELOCITY_THRESHOLD: vel_y_direction = 1
        elif self.velocity.y < -PLAYER_ANIMATION_VELOCITY_THRESHOLD: vel_y_direction = -1

        target_animation = None
        if vel_x_direction > 0: target_animation = "walk_right"
        elif vel_x_direction < 0: target_animation = "walk_left"
        elif vel_y_direction != 0 : target_animation = "idle_front" # Purely vertical or falling while x-idle
        else: target_animation = "idle_front" # Effectively still
        
        if target_animation and (self.current_animation_name != target_animation or not self.current_frames):
            self.set_animation(target_animation)

        if not self.current_frames: # If set_animation failed or no current_frames somehow
            if self.image is None: # Ensure self.image exists for drawing
                self.image = pygame.Surface((32 * self.scale_factor, 32 * self.scale_factor), pygame.SRCALPHA)
                self.image.fill((0,0,255,100)) # Blue placeholder if no animation
                if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
            return

        # Tick-based animation timing
        self.ticks_since_last_frame_change += 1
        if self.ticks_since_last_frame_change >= self.animation_ticks_per_frame:
            self.ticks_since_last_frame_change = 0 # Reset counter
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)
            
            # Ensure new frame index is valid before accessing (should always be if len > 0)
            if self.current_frame_index < len(self.current_frames) and self.current_frames[self.current_frame_index]:
                 new_image = self.current_frames[self.current_frame_index]
                 if self.rect is not None: 
                     old_center = self.rect.center
                     self.image = new_image
                     self.rect = self.image.get_rect(center=old_center)
                 else: # Should be rare if rect is initialized properly
                     self.image = new_image
                     self.rect = self.image.get_rect(topleft=self.position)

    def update(self, dt): # Player's main update method
        """
        Update the player state. Called once per game frame.
        Args:
            dt (float): Delta time for the current frame.
        """
        self.handle_input_and_movement(dt)
        self.update_animation()