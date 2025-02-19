import pygame


class Obstacle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.color = (255, 0, 0)  # Red

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class PowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.color = (0, 255, 0)  # Green

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
