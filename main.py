import pygame
import os

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)

# Asset paths
SPRITESHEET_BASENAME = "Amstrad CPC - Sorcery - Characters.png"
SPRITESHEET_FILENAME = os.path.join("assets", "images", SPRITESHEET_BASENAME)


# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Wizard Animation - Tick-Based Perfection")
clock = pygame.time.Clock()

# --- Spritesheet Class (remains the same) ---
class Spritesheet:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            print(f"Expected location: {os.path.abspath(filename)}")
            raise SystemExit(e)

    def get_image(self, x, y, width, height, scale=None):
        image = pygame.Surface([width, height], pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        if scale:
            image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        return image

    def get_animation_frames(self, start_x, y, frame_width, frame_height, num_frames, spacing=0, scale=None):
        frames = []
        current_x = start_x
        for _ in range(num_frames):
            frames.append(self.get_image(current_x, y, frame_width, frame_height, scale))
            current_x += frame_width + spacing
        return frames

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    # Changed: anim_speed (ms) replaced with animation_ticks_per_frame
    def __init__(self, spritesheet_obj, animation_frames_data, initial_animation, position=(100,100), animation_ticks_per_frame=7):
        super().__init__()
        self.spritesheet = spritesheet_obj
        self.animations = {}
        self.scale_factor = 3
        self.load_animations(animation_frames_data)

        self.current_animation_name = None
        self.current_frames = []
        self.current_frame_index = 0
        
        # New animation timing mechanism
        self.animation_ticks_per_frame = animation_ticks_per_frame
        self.ticks_since_last_frame_change = 0

        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(0, 0)

        self.speed_pps = 6 * FPS
        self.gravity_pps = 5 * FPS 

        self.is_on_ground = False

        self.image = None
        self.rect = None
        if initial_animation and self.animations.get(initial_animation):
            self.set_animation(initial_animation)
        else:
            print(f"Warning: Initial animation '{initial_animation}' failed or was empty, or no animations loaded.")
            self.image = pygame.Surface([32 * self.scale_factor, 32 * self.scale_factor], pygame.SRCALPHA)
            self.image.fill((255,0,0,128)) 
            self.rect = self.image.get_rect(topleft=position)
            if not self.animations:
                 print("CRITICAL: Animations dictionary is empty after Player init during fallback.")


    def load_animations(self, animation_frames_data):
        if not animation_frames_data:
            print("CRITICAL: animation_frames_data is empty in load_animations.")
            return
        for name, data in animation_frames_data.items():
            frames = self.spritesheet.get_animation_frames(
                data["x"], data["y"], data["w"], data["h"],
                data["count"], data.get("spacing", 0),
                scale=self.scale_factor
            )
            if not frames:
                print(f"Warning: No frames loaded for animation '{name}' in load_animations.")
            self.animations[name] = frames
        if not self.animations:
             print("CRITICAL: Animations dictionary is still empty after loading attempts.")


    def set_animation(self, animation_name):
        if self.current_animation_name == animation_name and self.current_frames:
            return

        # print(f"Setting animation from '{self.current_animation_name}' to '{animation_name}'") # Optional debug

        if not self.animations: # Should ideally not be hit if load_animations works
            print(f"CRITICAL: Attempting to set animation '{animation_name}', but self.animations is empty.")
            self.image = pygame.Surface((32*self.scale_factor, 32*self.scale_factor), pygame.SRCALPHA); self.image.fill((0,255,255,128))
            if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
            else: self.rect.size = self.image.get_size()
            self.current_frames = []; self.current_animation_name = None
            return

        if animation_name not in self.animations or not self.animations[animation_name]:
            print(f"Warning: Animation '{animation_name}' not found or has no frames.")
            if self.current_frames and self.current_animation_name: return
            self.image = pygame.Surface((32*self.scale_factor, 32*self.scale_factor), pygame.SRCALPHA); self.image.fill((255,255,0,128))
            if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
            else: self.rect.size = self.image.get_size()
            self.current_frames = []; self.current_animation_name = None
            return

        self.current_animation_name = animation_name
        self.current_frames = self.animations[animation_name]
        self.current_frame_index = 0
        self.ticks_since_last_frame_change = 0 # Reset tick counter for new animation

        if not self.current_frames:
            print(f"Warning: No frames assigned for animation: {animation_name} after set.")
            self.image = pygame.Surface((32*self.scale_factor, 32*self.scale_factor), pygame.SRCALPHA); self.image.fill((255,0,255,128))
            if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
            else: self.rect.size = self.image.get_size()
            return

        new_image = self.current_frames[self.current_frame_index]
        if self.rect is not None:
            current_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect(center=current_center)
        else:
            self.image = new_image
            self.rect = self.image.get_rect(topleft=self.position)


    def handle_input_and_movement(self, dt): # dt is still used for movement
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

        if self.image is None: # Fallback if image somehow becomes None
             self.image = pygame.Surface((32 * self.scale_factor, 32 * self.scale_factor), pygame.SRCALPHA); self.image.fill((255,165,0,128))
        if self.rect is None:
            self.rect = self.image.get_rect(topleft=self.position)
        else: # Ensure rect is updated if image exists
            self.rect.topleft = (round(self.position.x), round(self.position.y))


        # Boundary corrections
        corrected = False
        if self.rect.left < 0: self.position.x -= self.rect.left; corrected=True
        if self.rect.right > SCREEN_WIDTH: self.position.x -= (self.rect.right - SCREEN_WIDTH); corrected=True
        if self.rect.top < 0: self.position.y -= self.rect.top; corrected=True
        if self.rect.bottom > SCREEN_HEIGHT:
            self.position.y -= (self.rect.bottom - SCREEN_HEIGHT)
            self.is_on_ground = True
            corrected=True
        else:
            self.is_on_ground = False
        if corrected:
            self.rect.topleft = (round(self.position.x), round(self.position.y))


    def update_animation(self): # dt is NOT used here anymore for frame timing
        animation_velocity_threshold = 5.0
        vel_x_direction = 0
        if self.velocity.x > animation_velocity_threshold : vel_x_direction = 1
        elif self.velocity.x < -animation_velocity_threshold: vel_x_direction = -1
        vel_y_direction = 0
        if self.velocity.y > animation_velocity_threshold: vel_y_direction = 1
        elif self.velocity.y < -animation_velocity_threshold: vel_y_direction = -1

        target_animation = None
        if vel_x_direction > 0: target_animation = "walk_right"
        elif vel_x_direction < 0: target_animation = "walk_left"
        elif vel_y_direction != 0 : target_animation = "idle_front"
        else: target_animation = "idle_front"
        
        if target_animation and (self.current_animation_name != target_animation or not self.current_frames):
            self.set_animation(target_animation)

        if not self.current_frames:
            if self.image is None:
                self.image = pygame.Surface((32 * self.scale_factor, 32 * self.scale_factor), pygame.SRCALPHA); self.image.fill((0,0,255,100))
                if self.rect is None: self.rect = self.image.get_rect(topleft=self.position)
            return

        # New tick-based animation timing
        self.ticks_since_last_frame_change += 1
        if self.ticks_since_last_frame_change >= self.animation_ticks_per_frame:
            self.ticks_since_last_frame_change = 0 # Reset counter
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)
            
            if self.current_frame_index < len(self.current_frames) and self.current_frames[self.current_frame_index]:
                 new_image = self.current_frames[self.current_frame_index]
                 if self.rect is not None:
                     old_center = self.rect.center
                     self.image = new_image
                     self.rect = self.image.get_rect(center=old_center)
                 else:
                     self.image = new_image
                     self.rect = self.image.get_rect(topleft=self.position)

    def update(self, dt): # dt is passed for movement
        self.handle_input_and_movement(dt)
        self.update_animation() # update_animation no longer uses dt directly

# --- Game Setup ---
try:
    my_spritesheet = Spritesheet(SPRITESHEET_FILENAME)
except SystemExit: pygame.quit(); exit()

wizard_animations_data = {
    "walk_left":  { "x": 0,   "y": 75, "w": 24, "h": 24, "count": 4, "spacing": 1},
    "idle_front": { "x": 100, "y": 75, "w": 24, "h": 24, "count": 4, "spacing": 1},
    "walk_right": { "x": 200, "y": 75, "w": 24, "h": 24, "count": 4, "spacing": 1}
}

player_start_pos = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)
try:
    # EXPERIMENT HERE: Try 7 or 8 for animation_ticks_per_frame
    wizard = Player(my_spritesheet, wizard_animations_data,
                    initial_animation="idle_front",
                    position=player_start_pos,
                    animation_ticks_per_frame=7) # Defaulting to 7, try 8!
    if not wizard.animations: print("CRITICAL: Player animations empty after creation.")
    all_sprites = pygame.sprite.Group()
    all_sprites.add(wizard)
except Exception as e:
    print(f"Error creating Player or adding to sprite group: {e}"); pygame.quit(); exit()

# --- Game Loop ---
running = True
frame_count = 0 # For dt spike check, can be removed if confident
while running:
    dt = clock.tick(FPS) / 1000.0 # dt is still important for movement and game pacing
    frame_count += 1

    # Optional DT Spike Check (can be removed if you're sure dt is stable)
    # expected_dt = 1.0 / FPS
    # if frame_count > FPS * 2 and dt > expected_dt * 1.5:
    #     print(f"High dt spike: {dt*1000:.2f}ms (Expected: {expected_dt*1000:.2f}ms) at game time {pygame.time.get_ticks()}ms")

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        # You could add key presses here to change wizard.animation_ticks_per_frame at runtime for quick testing
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                wizard.animation_ticks_per_frame = 7
                print("Animation speed: 7 ticks per frame")
            if event.key == pygame.K_2:
                wizard.animation_ticks_per_frame = 8
                print("Animation speed: 8 ticks per frame")
            if event.key == pygame.K_3:
                wizard.animation_ticks_per_frame = 6 # A bit faster
                print("Animation speed: 6 ticks per frame")


    if 'wizard' in locals() and wizard is not None and 'all_sprites' in locals():
        all_sprites.update(dt) # dt is passed to player.update
        screen.fill(BLACK)
        all_sprites.draw(screen)
    else: # Fallback rendering if player/group somehow missing
        screen.fill(BLACK) # Should not happen with current setup
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Error: Player or sprite group not initialized.", True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()

pygame.quit()