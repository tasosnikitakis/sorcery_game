# player.py

import pygame
from settings import (PLAYER_SCALE_FACTOR, PLAYER_ANIMATION_TICKS_PER_FRAME,
                      PLAYER_ANIMATION_VELOCITY_THRESHOLD, PLAYER_SPEED_PPS, PLAYER_GRAVITY_PPS,
                      SCREEN_WIDTH, GAME_AREA_HEIGHT) # <-- GAME_AREA_HEIGHT is correctly imported

class Player(pygame.sprite.Sprite):
    def __init__(self, spritesheet_obj, animation_frames_data, initial_animation, position=(100,100),
                 animation_ticks_per_frame=PLAYER_ANIMATION_TICKS_PER_FRAME):
        super().__init__()
        self.spritesheet = spritesheet_obj
        self.animations = {}
        self.scale_factor = PLAYER_SCALE_FACTOR
        self.load_animations(animation_frames_data)

        self.current_animation_name = None
        self.current_frames = []
        self.current_frame_index = 0
        
        self.animation_ticks_per_frame = animation_ticks_per_frame
        self.ticks_since_last_frame_change = 0

        self.position = pygame.math.Vector2(position) # Float-based position
        self.velocity = pygame.math.Vector2(0, 0)
        
        self.speed_pps = PLAYER_SPEED_PPS
        self.gravity_pps = PLAYER_GRAVITY_PPS

        self.is_on_ground = False # Will be set by collision logic

        self.image = None 
        self.rect = None 
        if initial_animation and self.animations.get(initial_animation):
            self.set_animation(initial_animation) 
        else:
            print(f"Warning: Initial animation '{initial_animation}' failed for Player.")
            self.image = pygame.Surface([32 * self.scale_factor, 32 * self.scale_factor], pygame.SRCALPHA)
            self.image.fill((255,0,0,128)) 
            self.rect = self.image.get_rect(topleft=position)
            if not self.animations: print("CRITICAL: Player animations empty after init fallback.")

    def load_animations(self, animation_frames_data):
        if not animation_frames_data: print("CRITICAL: animation_frames_data empty in Player.load_animations."); return
        for name, data in animation_frames_data.items():
            frames = self.spritesheet.get_animation_frames(
                data["x"], data["y"], data["w"], data["h"],
                data["count"], data.get("spacing", 0), scale=self.scale_factor)
            if not frames: print(f"Warning: No frames loaded for '{name}' in Player.load_animations.")
            self.animations[name] = frames
        if not self.animations: print("CRITICAL: Player animations still empty after loading.")

    def set_animation(self, animation_name):
        if self.current_animation_name == animation_name and self.current_frames: return
        if not self.animations: print(f"CRITICAL: No animations loaded when trying to set '{animation_name}'."); return

        target_frames = self.animations.get(animation_name)
        if not target_frames: # Animation name not found or frames list is empty
            print(f"Warning: Animation '{animation_name}' not found or empty. Attempting fallback or keeping current.")
            if self.current_frames and self.current_animation_name and self.animations.get(self.current_animation_name):
                # Keep current valid animation if the new one is invalid
                return 
            # If no valid current animation, try to set to any available default
            for anim_key, anim_frames_list in self.animations.items():
                if anim_frames_list: # Found a valid animation
                    print(f"Fallback: Setting to first available animation: '{anim_key}'")
                    self.current_animation_name = anim_key
                    self.current_frames = anim_frames_list
                    break 
            else: # No valid animations found at all for fallback
                print("CRITICAL: No valid animations available for fallback in set_animation.")
                self.image = pygame.Surface((32*self.scale_factor, 32*self.scale_factor), pygame.SRCALPHA); self.image.fill((255,255,0,128)) # Yellow
                if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
                else: self.rect.size = self.image.get_size()
                self.current_frames = []; self.current_animation_name = animation_name # Note intended name even if failed
                # Reset frame index and ticks for the fallback image/state
                self.current_frame_index = 0
                self.ticks_since_last_frame_change = 0
                return # Exit after setting fallback image
        else: # Successfully found the requested animation
            self.current_animation_name = animation_name
            self.current_frames = target_frames
        
        self.current_frame_index = 0
        self.ticks_since_last_frame_change = 0
            
        # Ensure current_frames is not empty before trying to access index 0
        if not self.current_frames:
             print(f"CRITICAL: current_frames for '{self.current_animation_name}' is unexpectedly empty after assignment.")
             # Handle this by setting a fallback image again, or ensuring an image exists
             self.image = pygame.Surface((32*self.scale_factor, 32*self.scale_factor), pygame.SRCALPHA); self.image.fill((255,0,255,128)) # Magenta
             if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
             else: self.rect.size = self.image.get_size()
             return

        new_image = self.current_frames[self.current_frame_index]
        if self.rect is not None:
            current_center = self.rect.center; self.image = new_image; self.rect = self.image.get_rect(center=current_center)
        else: 
            self.image = new_image; self.rect = self.image.get_rect(topleft=self.position)

    def handle_input_and_movement(self, dt):
        keys = pygame.key.get_pressed()
        
        moving_left = keys[pygame.K_LEFT]; moving_right = keys[pygame.K_RIGHT]
        
        target_horizontal_velocity = 0
        if moving_left and not moving_right: target_horizontal_velocity = -self.speed_pps
        elif moving_right and not moving_left: target_horizontal_velocity = self.speed_pps
        self.velocity.x = target_horizontal_velocity

        # Default to applying gravity
        current_vy = self.gravity_pps
        
        # Player input for vertical movement overrides gravity for this frame's calculation
        if keys[pygame.K_UP]: current_vy = -self.speed_pps
        elif keys[pygame.K_DOWN]: current_vy = self.speed_pps # Allow downward movement input
        
        # If on ground from previous frame and no explicit vertical input, velocity.y should be 0.
        # Gravity will be applied if is_on_ground becomes false (e.g. walks off a ledge).
        if self.is_on_ground and not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            self.velocity.y = 0 # Prevent gravity from building up if on ground and no input
        else:
            self.velocity.y = current_vy # Apply calculated vertical velocity (gravity or input)
        
        # Update float position based on velocity and dt
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        # self.rect and screen boundaries are handled in the main update() method after this

    def handle_platform_collisions(self, platforms):
        # Temporarily update self.rect to current self.position for collision checks
        # This rect represents the player's intended position *before* collision resolution for this axis
        if self.rect is None: # Should ideally always have a rect, but as a safeguard
            if self.image: self.rect = self.image.get_rect()
            else: self.rect = pygame.Rect(0,0, 32*self.scale_factor, 32*self.scale_factor) # Placeholder size
        
        self.rect.x = round(self.position.x)
        
        # Horizontal collision check
        hit_list_x = pygame.sprite.spritecollide(self, platforms, False)
        for platform_hit in hit_list_x:
            if self.velocity.x > 0: # Moving right; hit left side of platform
                self.rect.right = platform_hit.rect.left
            elif self.velocity.x < 0: # Moving left; hit right side of platform
                self.rect.left = platform_hit.rect.right
            self.position.x = float(self.rect.x) # Sync float position to corrected rect.x
            self.velocity.x = 0 # Stop horizontal movement

        # Vertical collision check
        self.rect.y = round(self.position.y) # Update rect y for vertical check
        
        # Important: Reset is_on_ground before vertical collision checks for the current frame.
        # It will be set to True if a downward collision with a platform occurs.
        # If the player was on the ground and moves upwards (e.g. jumps), 
        # this reset allows them to leave the ground.
        previous_is_on_ground = self.is_on_ground # Store state before reset for certain logic if needed
        self.is_on_ground = False 

        hit_list_y = pygame.sprite.spritecollide(self, platforms, False)
        for platform_hit in hit_list_y:
            if self.velocity.y > 0: # Moving down; hit top side of platform
                self.rect.bottom = platform_hit.rect.top
                self.is_on_ground = True
            elif self.velocity.y < 0: # Moving up; hit bottom side of platform
                self.rect.top = platform_hit.rect.bottom
            self.position.y = float(self.rect.y) # Sync float position to corrected rect.y
            self.velocity.y = 0 # Stop vertical movement

    def apply_screen_boundaries(self):
        # Use current self.rect (which should have been updated by platform collisions if any)
        # or direct self.position and its dimensions for clamping.
        if self.rect is None: # Should not happen if update logic is correct, but safeguard
            return

        current_rect_width = self.rect.width
        current_rect_height = self.rect.height

        # Clamp X position (Horizontal bounds still use SCREEN_WIDTH)
        if self.position.x < 0:
            self.position.x = 0
            if self.velocity.x < 0: self.velocity.x = 0
        elif self.position.x + current_rect_width > SCREEN_WIDTH:
            self.position.x = SCREEN_WIDTH - current_rect_width
            if self.velocity.x > 0: self.velocity.x = 0
        
        # Clamp Y position (Vertical bounds use GAME_AREA_HEIGHT for the bottom)
        if self.position.y < 0: # Top of the game area
            self.position.y = 0
            if self.velocity.y < 0: self.velocity.y = 0 # Hit screen top
        # --- ADJUSTMENT FOR GAME AREA ---
        # The player's bottom edge is checked against GAME_AREA_HEIGHT
        elif self.position.y + current_rect_height > GAME_AREA_HEIGHT:
            self.position.y = GAME_AREA_HEIGHT - current_rect_height
            # If not already on a platform from platform_collisions, 
            # hitting the bottom of the game area makes the player "on_ground".
            if not self.is_on_ground: 
                self.is_on_ground = True
            if self.velocity.y > 0: self.velocity.y = 0 # Hit game area bottom

    def update_animation(self):
        animation_velocity_threshold = PLAYER_ANIMATION_VELOCITY_THRESHOLD

        vel_x_direction = 0
        if self.velocity.x > animation_velocity_threshold : vel_x_direction = 1
        elif self.velocity.x < -animation_velocity_threshold: vel_x_direction = -1
        
        vel_y_direction = 0 
        # Consider falling if Y velocity is positive and not on ground
        if self.velocity.y > animation_velocity_threshold and not self.is_on_ground : vel_y_direction = 1 # Falling
        elif self.velocity.y < -animation_velocity_threshold: vel_y_direction = -1 # Going up (jumping)

        target_animation = None
        if vel_x_direction > 0: target_animation = "walk_right"
        elif vel_x_direction < 0: target_animation = "walk_left"
        # If primarily moving vertically (or falling), use idle_front or a dedicated jump/fall animation
        elif vel_y_direction != 0 : target_animation = "idle_front" # Placeholder for jump/fall
        else: target_animation = "idle_front" # Still (on ground or perfectly balanced mid-air with no x-mov)
        
        if target_animation and (self.current_animation_name != target_animation or not self.current_frames):
            self.set_animation(target_animation)

        if not self.current_frames:
            if self.image is None: # Ensure self.image exists if animation fails
                self.image = pygame.Surface((32 * self.scale_factor, 32 * self.scale_factor), pygame.SRCALPHA); self.image.fill((0,0,255,100)) # Blue placeholder
                if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
            return

        self.ticks_since_last_frame_change += 1
        if self.ticks_since_last_frame_change >= self.animation_ticks_per_frame:
            self.ticks_since_last_frame_change = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)
            
            if self.current_frame_index < len(self.current_frames) and self.current_frames[self.current_frame_index]:
                new_image = self.current_frames[self.current_frame_index]
                if self.rect is not None:
                    old_center = self.rect.center; self.image = new_image; self.rect = self.image.get_rect(center=old_center)
                else: # Should be initialized, but as a safeguard
                    self.image = new_image; self.rect = self.image.get_rect(topleft=self.position)

    def update(self, dt, platforms):
        # 1. Calculate intended self.position based on input, gravity, and dt
        self.handle_input_and_movement(dt)

        # Ensure self.rect is initialized before collision checks if it's somehow None
        if self.rect is None:
            if self.image: 
                self.rect = self.image.get_rect(topleft=(round(self.position.x), round(self.position.y)))
            else: # Absolute fallback: create a default rect based on position and default size
                 # This case implies image might also be None, so set_animation or __init__ might have issues
                print("Warning: Player rect was None and image was None during update. Creating default rect.")
                self.rect = pygame.Rect(round(self.position.x), round(self.position.y), 32 * self.scale_factor, 32 * self.scale_factor)

        # 2. Handle platform collisions:
        #    This adjusts self.rect, self.position, self.velocity, and self.is_on_ground
        self.handle_platform_collisions(platforms)
        
        # 3. Apply screen boundaries:
        #    This further adjusts self.position and self.velocity if hitting screen edges
        #    This is where GAME_AREA_HEIGHT is used for the bottom boundary.
        self.apply_screen_boundaries()

        # 4. Finalize self.rect's position based on the fully corrected self.position for drawing
        if self.rect is not None: # Ensure rect exists before assigning to its topleft
            self.rect.topleft = (round(self.position.x), round(self.position.y))
        
        # 5. Update animation based on final velocity and state
        self.update_animation() # Corrected: removed colon from method call