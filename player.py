import pygame
import math


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 80
        self.rect = pygame.Rect(x, y - self.height, self.width, self.height)

        # Load Sam Altman sprite
        self.sprite = None
        self.load_default_image()

        # Movement variables
        self.velocity_y = 0
        self.gravity = 0.8
        self.base_jump_power = -15
        self.jump_power = self.base_jump_power
        self.is_jumping = False
        self.ground_y = y

        # Added max velocity limit
        self.max_velocity_up = -10  # Maximum upward velocity
        self.max_velocity_down = 15  # Maximum downward velocity

        # Jetpack system variables
        self.jetpack_fuel = 50
        self.max_jetpack_fuel = 100
        self.fuel_consumption_rate = 15
        self.is_using_jetpack = False

        # New: Jetpack thrust control (reduced from original)
        self.jetpack_thrust = 0.4  # Reduced from original implied value

        # Animation variables
        self.animation_frame = 0
        self.animation_speed = 0.2

        # Special ability - quick dash
        self.can_dash = True
        self.dash_cooldown = 0
        self.is_dashing = False
        self.dash_duration = 0
        self.invincible = False
        self.invincible_timer = 0

    def load_default_image(self):
        try:
            # Try to load the sprite image - if it exists
            self.sprite = pygame.image.load(
                "assets/sam_altman.png").convert_alpha()
            self.sprite = pygame.transform.scale(
                self.sprite, (self.width, self.height))
        except:
            # Create a placeholder if image doesn't exist
            self.sprite = pygame.Surface(
                (self.width, self.height), pygame.SRCALPHA)
            self.sprite.fill((200, 150, 100))  # Placeholder color

    def load_grave_image(self):
        try:
            grave_path = "assets/grave.png"
            self.sprite = pygame.image.load(
                grave_path).convert_alpha()
            self.sprite = pygame.transform.scale(
                self.sprite, (self.width + 30, self.height + 20))
        except:
            print("Could not load grave image")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Jump with space (whether jetpack is enabled or not)
            if event.key == pygame.K_SPACE:
                if not self.is_using_jetpack and not self.is_jumping:
                    self.jump()
                # If jetpack is on, space will make it fly in the update method
            # Toggle jetpack with J
            elif event.key == pygame.K_j and self.jetpack_fuel >= 5:
                self.is_using_jetpack = not self.is_using_jetpack
            # Dash with D - inspired by Jetpack Joyride's utilities
            elif event.key == pygame.K_d and self.can_dash and not self.is_dashing:
                self.is_dashing = True
                self.dash_duration = 20  # frames
                self.can_dash = False
                self.dash_cooldown = 180  # 3 seconds cooldown
                self.invincible = True
                self.invincible_timer = 25  # slightly longer than dash

        # Turn off jetpack if run out of fuel
        if self.jetpack_fuel <= 0:
            self.is_using_jetpack = False

    def jump(self):
        self.velocity_y = self.jump_power
        self.is_jumping = True

    def update(self):
        # Handle dash cooldown
        if not self.can_dash:
            self.dash_cooldown -= 1
            if self.dash_cooldown <= 0:
                self.can_dash = True

        # Handle dash duration
        if self.is_dashing:
            self.dash_duration -= 1
            if self.dash_duration <= 0:
                self.is_dashing = False

        # Handle invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        # Handle jetpack with fuel system
        if self.is_using_jetpack and self.jetpack_fuel > 0:
            # Consume fuel while using jetpack
            self.jetpack_fuel -= self.fuel_consumption_rate / 60

            # Check if space bar is held down for flying upward
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                # Add an initial lift if player is on the ground
                if self.rect.bottom >= self.ground_y:
                    self.velocity_y = -5  # Initial upward boost to get off the ground

                # Apply controlled upward thrust with more gentle acceleration
                self.velocity_y -= self.jetpack_thrust

                # Cap upward velocity to prevent flying too fast
                if self.velocity_y < self.max_velocity_up:
                    self.velocity_y = self.max_velocity_up

                # Ensure player doesn't fly too high
                if self.rect.top <= 50:  # Allow a small margin at the top
                    self.rect.top = 50
                    self.velocity_y = 0
            else:
                # Apply reduced gravity if space bar is not held
                self.velocity_y += self.gravity * 0.3
        else:
            # Apply normal gravity when not using jetpack
            self.velocity_y += self.gravity

        # Cap downward velocity to prevent falling too fast
        if self.velocity_y > self.max_velocity_down:
            self.velocity_y = self.max_velocity_down

        # Apply velocity
        self.rect.y += self.velocity_y

        # Check ground collision
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.velocity_y = 0
            self.is_jumping = False

        # Update animation frame
        self.animation_frame += self.animation_speed
        if self.animation_frame >= 4:
            self.animation_frame = 0

    def add_fuel(self, amount):
        self.jetpack_fuel += amount
        if self.jetpack_fuel > self.max_jetpack_fuel:
            self.jetpack_fuel = self.max_jetpack_fuel

    def draw(self, screen):
        if self.sprite:
            # Use sprite if available, apply transparency for invincibility
            sprite_copy = self.sprite.copy()
            if self.invincible and int(self.animation_frame * 4) % 2 == 0:
                # Make sprite semi-transparent when invincible
                sprite_copy.set_alpha(128)
            screen.blit(sprite_copy, self.rect)
        else:
            # Fallback to drawing placeholder
            color = (200, 150, 100)
            if self.invincible and int(self.animation_frame * 4) % 2 == 0:
                color = (255, 255, 255)
            pygame.draw.rect(screen, color, self.rect)

            # Draw eyes (simple face for placeholder)
            eye_color = (50, 50, 200)
            pygame.draw.circle(screen, eye_color,
                               (self.rect.x + 15, self.rect.y + 20), 5)
            pygame.draw.circle(screen, eye_color,
                               (self.rect.x + 35, self.rect.y + 20), 5)

        # Dashing effect
        if self.is_dashing:
            pygame.draw.rect(screen, (255, 200, 0),
                             (self.rect.x - 20, self.rect.y, 20, self.rect.height))

        # Draw jetpack if active
        if self.is_using_jetpack:
            jetpack_color = (200, 100, 0)
            pygame.draw.rect(screen, jetpack_color,
                             (self.rect.x - 10, self.rect.y + 30, 10, 20))

            # Draw flame
            flame_height = 15 + int(self.animation_frame * 10) % 15
            pygame.draw.polygon(screen, (255, 200, 0), [
                (self.rect.x - 10, self.rect.y + 50),
                (self.rect.x - 5, self.rect.y + 50 + flame_height),
                (self.rect.x, self.rect.y + 50)
            ])

        # Draw fuel bar above player
        fuel_bar_width = 50
        fuel_bar_height = 5
        fuel_fill = (self.jetpack_fuel / self.max_jetpack_fuel) * \
            fuel_bar_width

        # Empty bar background
        pygame.draw.rect(screen, (100, 100, 100),
                         (self.rect.x, self.rect.y - 10, fuel_bar_width, fuel_bar_height))

        # Filled portion of fuel bar
        fuel_color = (255, 150, 0) if self.is_using_jetpack else (255, 200, 0)
        pygame.draw.rect(screen, fuel_color,
                         (self.rect.x, self.rect.y - 10, fuel_fill, fuel_bar_height))

        # Draw dash cooldown indicator
        if not self.can_dash:
            cooldown_pct = self.dash_cooldown / 180
            pygame.draw.arc(screen, (150, 150, 150),
                            (self.rect.x + self.rect.width -
                             15, self.rect.y - 15, 10, 10),
                            0, cooldown_pct * 6.28, 3)
        else:
            pygame.draw.circle(screen, (0, 200, 0),
                               (self.rect.x + self.rect.width - 10, self.rect.y - 10), 5)
