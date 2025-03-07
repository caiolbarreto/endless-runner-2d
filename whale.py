import pygame
import math
import random


class Whale:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # The whale is pursuing the player
        self.x = -200  # Start off-screen
        self.y = height - 200
        self.rect = pygame.Rect(self.x, self.y, 180, 120)

        # Whale movement
        self.base_distance = 300  # Distance from left edge
        self.pursuit_speed = 0.5
        self.current_distance = self.base_distance
        self.vertical_offset = 0
        self.vertical_direction = 1
        self.animation_frame = 0

        # Sprite placeholder
        self.sprite = None
        self.try_load_sprite()

        # Default color if no sprite
        self.color = (80, 120, 255)  # Blue whale

    def try_load_sprite(self):
        try:
            # Try to load the sprite image - if it exists
            self.sprite = pygame.image.load("assets/whale.png").convert_alpha()
            self.sprite = pygame.transform.scale(
                self.sprite, (self.rect.width, self.rect.height))
        except:
            # No sprite available, will use drawn shape
            self.sprite = None

    def update(self, player_x, game_speed):
        # The whale follows the player but stays at a distance
        target_x = player_x - self.base_distance - (game_speed * 20)

        # Smooth pursuit
        self.x += (target_x - self.x) * self.pursuit_speed
        self.rect.x = int(self.x)

        # Vertical bobbing movement
        self.vertical_offset += 0.05 * self.vertical_direction
        if abs(self.vertical_offset) > 15:
            self.vertical_direction *= -1

        self.rect.y = self.y + int(self.vertical_offset)

        # Animation
        self.animation_frame += 0.1
        if self.animation_frame >= 4:
            self.animation_frame = 0

    def draw(self, screen):
        if self.sprite:
            # Use sprite if available
            screen.blit(self.sprite, self.rect)
        else:
            # Draw whale body
            pygame.draw.ellipse(screen, self.color, self.rect)

            # Draw eye
            eye_x = self.rect.x + self.rect.width - 40
            eye_y = self.rect.y + 30
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 15)
            pygame.draw.circle(screen, (0, 0, 0), (eye_x + 5, eye_y), 8)

            # Draw tail
            tail_x = self.rect.x
            tail_y = self.rect.y + 40
            tail_height = 60 + int(10 * math.sin(self.animation_frame))

            pygame.draw.polygon(screen, self.color, [
                (tail_x, tail_y),
                (tail_x - 40, tail_y - tail_height/2),
                (tail_x - 40, tail_y + tail_height/2)
            ])

        # Draw water splash effect
        splash_height = 5 + int(5 * math.sin(self.animation_frame * 2))
        for i in range(5):
            x_pos = self.rect.x + 20 + i * 30
            height = splash_height + random.randint(0, 10)
            pygame.draw.line(screen, (200, 230, 255),
                             (x_pos, self.rect.y + self.rect.height),
                             (x_pos, self.rect.y + self.rect.height + height), 3)
