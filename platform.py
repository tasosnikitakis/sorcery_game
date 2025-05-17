# platform.py

import pygame
from settings import  WHITE# Using a default color from settings

class Platform(pygame.sprite.Sprite):
    """
    Represents a solid platform in the game world.
    """
    def __init__(self, x, y, width, height, color=None):
        """
        Initializes a new platform.
        Args:
            x (int): The x-coordinate of the platform's top-left corner.
            y (int): The y-coordinate of the platform's top-left corner.
            width (int): The width of the platform.
            height (int): The height of the platform.
            color (tuple, optional): The RGB color of the platform. 
                                     Defaults to BLACK from settings.py.
        """
        super().__init__() # Call the parent class (Sprite) constructor

        self.image = pygame.Surface([width, height])
        if color is None:
            self.image.fill(WHITE) # Default color
        else:
            self.image.fill(color)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # --- Add this line to create a mask for the platform ---
        self.mask = pygame.mask.from_surface(self.image)
        # --- End of new line ---

    # Platforms are static, so their update() method doesn't need to do anything
    # unless you want moving platforms later.
    # def update(self, *args):
    #     pass