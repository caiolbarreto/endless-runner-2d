import pygame


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.color = (0, 0, 255)  # Blue

        # Movement variables
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_power = -15
        self.is_jumping = False
        self.ground_y = y

        # Fly power-up variables
        self.fly_power_active = False
        self.fly_power_duration = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.is_jumping:
                self.jump()

    def jump(self):
        if not self.fly_power_active:
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def update(self):
        # Apply gravity if not flying
        if not self.fly_power_active:
            self.velocity_y += self.gravity
        else:
            # Check if space bar is held down for flying
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                if self.rect.top > 0:  # Ceiling
                    self.velocity_y -= self.gravity + 0.0025  # Fly upwards
                else:
                    self.rect.top = 0
                    self.velocity_y = 0
            else:
                self.velocity_y += (
                    self.gravity
                )  # Apply gravity if space bar is not held

        self.rect.y += self.velocity_y

        # Check ground collision
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.velocity_y = 0
            self.is_jumping = False

        # Update fly power-up duration
        if self.fly_power_active:
            self.fly_power_duration -= 1 / 60  # Decrease duration over time
            if self.fly_power_duration <= 0:
                self.fly_power_active = False

    def activate_fly_power(self, duration):
        self.fly_power_active = True
        self.fly_power_duration = duration

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
