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
        

class MagnetPowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.color = (200, 50, 50)  # Red magnet
        self.duration = 10  # Seconds

    def update(self, speed):
        # Move left with the game speed
        self.rect.x -= speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)  # Magnet body
        pygame.draw.line(screen, (0, 0, 0), (self.rect.centerx - 10, self.rect.centery),
                         (self.rect.centerx + 10, self.rect.centery), 3)  # Magnet poles
        
class DoublePointsPowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)  # Hitbox for collision
        self.color = (255, 215, 0)  # Gold color for the coin
        self.points = random.randint(5, 15) * 10  # Points awarded
        self.duration = 10  # Duration of the double points effect in seconds

        # Rotation animation (slower)
        self.angle = 0
        self.rotation_speed = random.uniform(1, 2)  # Reduced rotation speed

        # Floating animation (slower)
        self.base_y = y
        self.float_offset = 0
        self.float_speed = random.uniform(0.01, 0.03)  # Reduced floating speed

    def update(self, speed):
        # Move left with the game speed (slower)
        self.rect.x -= speed * 0.5  # Reduced movement speed (80% of game speed)

        # Rotation animation
        self.angle += self.rotation_speed
        if self.angle >= 360:
            self.angle = 0

        # Floating animation
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 8  # Reduced amplitude
        self.rect.y = self.base_y + int(self.float_offset)

    def draw(self, screen):
        # Draw the coin (golden circle)
        pygame.draw.circle(screen, self.color, self.rect.center, 15)

        # Draw the "$" symbol in the center
        font = pygame.font.Font(None, 30)  # Use a smaller font for the symbol
        text = font.render("$", True, (255, 255, 255))  # White "$" symbol
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

class FlyingDrone:
    def __init__(self, x, y, game_height):
        self.rect = pygame.Rect(x, y, 40, 40)  # Hitbox for collision
        self.game_height = game_height  # Store game height for bounds checking
        self.speed_x = random.choice([-2, 2])  # Horizontal movement
        self.speed_y = random.choice([-2, 2])  # Vertical movement

    def update(self, game_speed):
        self.rect.x -= game_speed  # Move left with the game
        self.rect.x += self.speed_x  # Horizontal movement
        self.rect.y += self.speed_y  # Vertical movement

        # Keep drone within screen bounds
        if self.rect.top < 100:  # Don't go too high
            self.rect.top = 100
            self.speed_y *= -1
        if self.rect.bottom > self.game_height - 50:  # Don't go too low
            self.rect.bottom = self.game_height - 50
            self.speed_y *= -1

    def draw(self, screen):
        # Drone body (central circle)
        pygame.draw.circle(screen, (100, 100, 100), self.rect.center, 15)  # Gray body

        # Propellers (4 small circles)
        propeller_color = (150, 150, 150)  # Dark gray
        pygame.draw.circle(screen, propeller_color, (self.rect.centerx - 20, self.rect.centery), 5)  # Left
        pygame.draw.circle(screen, propeller_color, (self.rect.centerx + 20, self.rect.centery), 5)  # Right
        pygame.draw.circle(screen, propeller_color, (self.rect.centerx, self.rect.centery - 20), 5)  # Top
        pygame.draw.circle(screen, propeller_color, (self.rect.centerx, self.rect.centery + 20), 5)  # Bottom

        # Lights (small colored circles)
        pygame.draw.circle(screen, (255, 0, 0), (self.rect.centerx - 10, self.rect.centery - 10), 3)  # Red light
        pygame.draw.circle(screen, (0, 255, 0), (self.rect.centerx + 10, self.rect.centery - 10), 3)  # Green light



class TimeSlowPowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 30)  # Hitbox for collision
        self.color = (50, 50, 200)  # Blue color for the watch
        self.duration = 5  # Duration of the time slow effect in seconds

        # Animation variables
        self.angle = 0  # For rotating clock hands
        self.rotation_speed = 2  # Speed of clock hand rotation

    def update(self, speed):
        # Move left with the game speed
        self.rect.x -= speed

        # Rotate the clock hands
        self.angle += self.rotation_speed
        if self.angle >= 360:
            self.angle = 0

    def draw(self, screen):
        # Draw the watch body (circle)
        pygame.draw.circle(screen, self.color, self.rect.center, 15)

        # Draw the clock face (inner circle)
        pygame.draw.circle(screen, (200, 200, 255), self.rect.center, 12)

        # Draw the clock hands
        # Hour hand
        hour_hand_length = 8
        hour_hand_angle = math.radians(self.angle)
        hour_hand_end = (
            self.rect.centerx + hour_hand_length * math.cos(hour_hand_angle),
            self.rect.centery - hour_hand_length * math.sin(hour_hand_angle)
        )
        pygame.draw.line(screen, (0, 0, 0), self.rect.center, hour_hand_end, 2)

        # Minute hand
        minute_hand_length = 12
        minute_hand_angle = math.radians(self.angle * 2)  # Rotate faster
        minute_hand_end = (
            self.rect.centerx + minute_hand_length * math.cos(minute_hand_angle),
            self.rect.centery - minute_hand_length * math.sin(minute_hand_angle)
        )
        pygame.draw.line(screen, (0, 0, 0), self.rect.center, minute_hand_end, 2)



class LaserBeam:
    def __init__(self, x, y, game_width):
        self.rect = pygame.Rect(x, y, game_width, 5)  # Thin beam spanning the screen width
        self.color = (255, 0, 0)  # Red laser
        self.active = False
        self.timer = 0

    def update(self, game_speed):
        if not self.active:
            self.timer += 1
            if self.timer >= 60:  # Activate after 1 second
                self.active = True
        else:
            self.rect.x -= game_speed  # Move left with the game

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)  # Draw laser

