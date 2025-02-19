import pygame
import sys
from player import Player
from game_objects import Obstacle, PowerUp
import random


class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Endless Runner")

        # Initialize clock
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # Create player
        self.player = Player(100, self.HEIGHT - 100)

        # Game objects
        self.obstacles = []
        self.powerups = []

        # Game state
        self.score = 0
        self.game_speed = 5
        self.spawn_timer = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            self.player.handle_event(event)
        return True

    def spawn_objects(self):
        self.spawn_timer += 1
        if self.spawn_timer >= 60:  # Spawn every second
            self.spawn_timer = 0
            if random.random() < 0.7:  # 70% chance for obstacle
                self.obstacles.append(Obstacle(self.WIDTH, self.HEIGHT - 50))
            elif random.random() < 0.3:  # 30% chance for power-up
                self.powerups.append(PowerUp(self.WIDTH, self.HEIGHT - 100))

    def update(self):
        # Update player
        self.player.update()

        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(self.game_speed)
            if obstacle.rect.right < 0:
                self.obstacles.remove(obstacle)
                self.score += 1

            # Collision detection
            if self.player.rect.colliderect(obstacle.rect):
                print(f"Game Over! Score: {self.score}")
                return False

        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update(self.game_speed)
            if powerup.rect.right < 0:
                self.powerups.remove(powerup)

            # Collision detection
            if self.player.rect.colliderect(powerup.rect):
                self.powerups.remove(powerup)
                self.game_speed -= 1  # Slow down game
                self.player.jump_power += 1  # Increase jump power

        # Increase game speed gradually
        if self.score % 10 == 0 and self.score > 0:
            self.game_speed += 0.1

        return True

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background

        # Draw player
        self.player.draw(self.screen)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.spawn_objects()
            running = self.update() and running
            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
