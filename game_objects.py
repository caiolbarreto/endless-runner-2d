import pygame
import random
import math


class Obstacle:
    def __init__(self, x, y):
        # Randomize obstacle appearance
        self.type = random.choice(["server", "competitor", "regulation"])

        # Set size based on type
        if self.type == "server":
            width = 30
            height = random.randint(60, 90)
            self.color = (150, 150, 150)  # Gray for servers
        elif self.type == "competitor":
            width = 40
            height = random.randint(40, 70)
            self.color = (150, 0, 0)  # Red for competitors
        else:  # regulation
            width = 50
            height = random.randint(30, 50)
            self.color = (0, 0, 150)  # Blue for regulations

        # Adjust to sit on ground correctly
        # This places the bottom of the obstacle at ground level (y)
        self.rect = pygame.Rect(x, y - height, width, height)

        # Animation variables
        self.animation_frame = 0
        self.animation_speed = 0.1

    def update(self, speed):
        self.rect.x -= speed

        # Simple animation
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 4:
            self.animation_frame = 0

    def draw(self, screen):
        # Draw base obstacle
        pygame.draw.rect(screen, self.color, self.rect)

        # Add details based on type
        if self.type == "server":
            # Draw server lights
            light_color = (0, 255, 0) if int(
                self.animation_frame * 4) % 2 == 0 else (255, 0, 0)
            pygame.draw.circle(screen, light_color,
                               (self.rect.x + self.rect.width//2, self.rect.y + 10), 3)

        elif self.type == "competitor":
            # Draw competitor logo
            pygame.draw.line(screen, (255, 255, 255),
                             (self.rect.x + 10, self.rect.y + 15),
                             (self.rect.x + self.rect.width - 10, self.rect.y + 15), 2)

        else:  # regulation
            # Draw regulation symbol
            pygame.draw.line(screen, (255, 255, 255),
                             (self.rect.x + 10, self.rect.y + 10),
                             (self.rect.x + self.rect.width - 10, self.rect.y + 25), 2)
            pygame.draw.line(screen, (255, 255, 255),
                             (self.rect.x + 10, self.rect.y + 25),
                             (self.rect.x + self.rect.width - 10, self.rect.y + 10), 2)


class JetpackFuel:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.color = (255, 150, 0)  # Orange
        self.fuel_amount = random.randint(20, 35)

        # Floating animation
        self.base_y = y
        self.float_offset = 0
        self.float_speed = random.uniform(0.05, 0.1)

    def update(self, speed):
        self.rect.x -= speed

        # Floating effect
        self.float_offset = math.sin(
            pygame.time.get_ticks() * self.float_speed) * 8
        self.rect.y = self.base_y + int(self.float_offset)

    def draw(self, screen):
        # Draw as a fuel canister
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)

        # Draw fuel symbol
        pygame.draw.line(screen, (255, 255, 255),
                         (self.rect.centerx, self.rect.y + 5),
                         (self.rect.centerx, self.rect.y + self.rect.height - 5), 2)
        pygame.draw.line(screen, (255, 255, 255),
                         (self.rect.centerx - 5, self.rect.y + 10),
                         (self.rect.centerx + 5, self.rect.y + 10), 2)


class InvestmentBonus:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.color = (50, 200, 50)  # Green
        self.points = random.randint(5, 15) * 10

        # Rotation animation
        self.angle = 0
        self.rotation_speed = random.uniform(2, 4)

        # Floating animation
        self.base_y = y
        self.float_offset = 0
        self.float_speed = random.uniform(0.03, 0.07)

    def update(self, speed):
        self.rect.x -= speed

        # Rotation
        self.angle += self.rotation_speed
        if self.angle >= 360:
            self.angle = 0

        # Floating effect
        self.float_offset = math.sin(
            pygame.time.get_ticks() * self.float_speed) * 10
        self.rect.y = self.base_y + int(self.float_offset)

    def draw(self, screen):
        # Draw as a dollar sign
        pygame.draw.circle(screen, self.color,
                           (self.rect.centerx, self.rect.centery), 15)

        # Draw $ symbol
        font = pygame.font.Font(None, 30)
        text = font.render("$", True, (255, 255, 255))
        text_rect = text.get_rect(
            center=(self.rect.centerx, self.rect.centery))
        screen.blit(text, text_rect)


class ShieldPowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.color = (100, 100, 255)  # Blue
        self.duration = 8  # seconds

        # Shield animation
        self.pulse = 0
        self.pulse_direction = 1

    def update(self, speed):
        self.rect.x -= speed

        # Pulsing effect
        self.pulse += 0.1 * self.pulse_direction
        if self.pulse >= 1 or self.pulse <= 0:
            self.pulse_direction *= -1

    def draw(self, screen):
        # Draw as a shield
        size = 12 + int(self.pulse * 3)
        pygame.draw.circle(screen, self.color,
                           (self.rect.centerx, self.rect.centery), size, width=3)

        # Inner circle
        pygame.draw.circle(screen, (200, 200, 255),
                           (self.rect.centerx, self.rect.centery), 8)
