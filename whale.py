import math
import random

import pygame


class Whale:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # The whale is pursuing the player
        self.x = -200  # Start off-screen
        self.y = height - 200
        self.rect = pygame.Rect(self.x, self.y, 90, 60)

        # Whale movement
        self.base_distance = 300  # Distance from left edge
        self.pursuit_speed = 0.5
        self.current_distance = self.base_distance
        self.vertical_offset = 0
        self.vertical_direction = 1
        self.horizontal_offset = 0
        self.horizontal_direction = 1
        self.animation_frame = 0

        self.state = "inactive"  # inactive, appearing, leaving
        self.timer = 0

        self.visible_duration = 130
        self.appear_cooldown = 130

        self.speed_x = 6

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
                self.sprite, (self.rect.width, self.rect.height)
            )
            self.sprite = pygame.transform.flip(self.sprite, True, False)

        except:
            # No sprite available, will use drawn shape
            self.sprite = None

    def update(self, player_x, game_speed):
        self.timer += 1

        if self.state == "inactive":
            if self.timer >= self.appear_cooldown:
                self.timer = 0
                self.state = "moving_in"
                self.visible = True

                self.x = -self.rect.width
                self.y = self.height - 110
                self.target_x = player_x - 120

        elif self.state == "moving_in":
            if self.x < self.target_x:
                self.x += self.speed_x
            else:
                self.x = self.target_x
                self.state = "waiting"
                self.timer = 0

        elif self.state == "waiting":
            if self.timer >= self.visible_duration:
                self.state = "moving_out"

        elif self.state == "moving_out":
            self.x -= self.speed_x
            if self.x + self.rect.width < 0:
                self.visible = False
                self.state = "inactive"
                self.timer = 0

        self.vertical_offset += 0.05 * self.vertical_direction
        if abs(self.vertical_offset) > 15:
            self.vertical_direction *= -1

        self.rect.x = int(self.x)
        self.rect.y = int(self.y + self.vertical_offset)

        self.animation_frame += 0.1
        if self.animation_frame >= 4:
            self.animation_frame = 0

    def draw(self, screen):
        if self.sprite:
            screen.blit(self.sprite, self.rect)
        else:
            # Draw whale shape
            pygame.draw.ellipse(screen, self.color, self.rect)

            # Eye
            eye_x = self.rect.x + self.rect.width - 40
            eye_y = self.rect.y + 30
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 15)
            pygame.draw.circle(screen, (0, 0, 0), (eye_x + 5, eye_y), 8)

            # Tail
            tail_x = self.rect.x
            tail_y = self.rect.y + 40
            tail_height = 60 + int(10 * math.sin(self.animation_frame))
            pygame.draw.polygon(
                screen,
                self.color,
                [
                    (tail_x, tail_y),
                    (tail_x - 40, tail_y - tail_height / 2),
                    (tail_x - 40, tail_y + tail_height / 2),
                ],
            )

        # Splash effect
        splash_height = 2 + int(3 * math.sin(self.animation_frame * 2))
        for i in range(3):
            x_pos = self.rect.x + 10 + i * 20
            height = splash_height + random.randint(0, 4)
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (x_pos, self.rect.y + self.rect.height),
                (x_pos, self.rect.y + self.rect.height + height),
                2,
            )
