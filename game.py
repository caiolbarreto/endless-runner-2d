import math
import os
import random
import sys

import pygame

from game_objects import (
    DeepfakePowerUp,
    DoublePointsPowerUp,
    FlyingDrone,
    InvestmentBonus,
    JetpackFuel,
    LaserBeam,
    MagnetPowerUp,
    Obstacle,
    ShieldPowerUp,
    TimeSlowPowerUp,
)
from player import Player
from whale import Whale


class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1200
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Sam Altman's DeepSeek Escape")

        # Initialize clock
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # Create assets folder if it doesn't exist
        os.makedirs("assets", exist_ok=True)

        # Load background images/layers for parallax
        self.backgrounds = self.load_backgrounds()
        self.bg_positions = [0, 0, 0]

        # Create player (Sam Altman)
        self.player = Player(125, self.HEIGHT - 50)

        # Create the pursuing whale (DeepSeek)
        self.whale = Whale(self.WIDTH, self.HEIGHT)

        # Game objects
        self.obstacles = []
        self.powerups = []

        # Add decorative elements lists
        self.clouds = []
        self.trees = []

        # Spawn rates for decorative elements
        self.cloud_spawn_timer = 0
        self.tree_spawn_timer = 0

        self.deepfake_chance = 0.2  # 20% de chance de um power-up ser um deepfake
        self.glitch_sound = None

        try:
            cloud_original = pygame.image.load(
                "assets/cloud.png").convert_alpha()
            tree_original = pygame.image.load(
                "assets/tree.png").convert_alpha()

            cloud_width = int(cloud_original.get_width() * 0.3)
            cloud_height = int(cloud_original.get_height() * 0.3)
            tree_width = int(tree_original.get_width() * 0.2)
            tree_height = int(tree_original.get_height() * 0.2)

            self.cloud_image = pygame.transform.scale(
                cloud_original, (cloud_width, cloud_height))
            self.tree_image = pygame.transform.scale(
                tree_original, (tree_width, tree_height))
        except:
            print("Warning: Could not load cloud or tree assets")
            self.cloud_image = None
            self.tree_image = None

        # Game state
        self.score = 0
        self.distance = 0
        self.base_game_speed = 7
        self.game_speed = self.base_game_speed
        self.max_game_speed = 12
        self.spawn_timer = 0

        # Shield effect (from power-up)
        self.shield_active = False
        self.shield_timer = 0

        # Game difficulty management
        self.difficulty_level = 1
        self.obstacle_chance = 0.5  # Starting chance
        self.obstacle_gap = 300
        self.next_milestone = 500  # Distance for next difficulty increase

        # Font for game information
        self.font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 36)
        self.small_font = pygame.font.Font("assets/fonts/ShareTechMono-Regular.ttf", 24)

        # Game over state
        self.game_over = False
        self.game_over_delay = 180  # 3 seconds before restart option

        # Load sounds (placeholders)
        self.sounds = self.load_sounds()

        self.slow_timer = 0  # Timer for time slow power-up
        self.magnet_active = False  # Whether the magnet power-up is active
        self.magnet_timer = 0  # Timer for magnet power-up
        self.double_points_active = False  # Whether double points power-up is active
        self.double_points_timer = 0  # Timer for double points power-up

    def load_backgrounds(self):
        """Load or create background layers for parallax effect"""
        backgrounds = [
            {"img": None, "speed": 0.5},
            {"img": None, "speed": 1.0},
            {"img": None, "speed": 2.0}
        ]

        # Try to load background images if they exist
        try:
            backgrounds[0]["img"] = pygame.image.load(
                "assets/background.png").convert()
            backgrounds[1]["img"] = pygame.image.load(
                "assets/background.png").convert()
            backgrounds[2]["img"] = pygame.image.load(
                "assets/background.png").convert()
            
        except:
            # Create solid color backgrounds if images don't exist
            for i, bg in enumerate(backgrounds):
                bg["img"] = pygame.Surface((self.WIDTH, self.HEIGHT))
                if i == 0:
                    bg["img"].fill((200, 230, 255))  # Sky
                elif i == 1:
                    bg["img"].fill((100, 180, 255))  # Mid layer
                else:
                    bg["img"].fill((50, 100, 200))   # Foreground

        return backgrounds

    def load_sounds(self):
        """Load game sounds if available"""
        sounds = {
            "jump": None,
            "jetpack": None,
            "pickup": None,
            "crash": None,
            "whale": None
        }

        try:
            pygame.mixer.init()
            # Load sounds if files exist
            for sound_name in sounds:
                try:
                    sounds[sound_name] = pygame.mixer.Sound(
                        f"assets/{sound_name}.wav")
                except:
                    # Skip if sound file doesn't exist
                    pass
        except:
            print("Sound system not available")

        return sounds

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if not self.game_over:
                self.player.handle_event(event)
            else:
                # Handle restart on game over
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game_over_delay <= 0:
                    self.reset_game()

        return True

    def reset_game(self):
        # Reset game state
        self.game_over = False
        self.score = 0
        self.distance = 0
        self.game_speed = self.base_game_speed

        # Reset player
        self.player = Player(125, self.HEIGHT - 50)

        # Reset whale
        self.whale = Whale(self.WIDTH, self.HEIGHT)

        # Clear objects
        self.obstacles = []
        self.powerups = []

        # Reset difficulty
        self.difficulty_level = 1
        self.obstacle_chance = 0.5
        self.next_milestone = 500

    def spawn_objects(self):
        self.spawn_timer += 1

        # Create a variable spawn rate that depends on game speed
        spawn_rate = max(20, 50 - self.game_speed * 2)

        # Check if any obstacle is too close to the right edge
        rightmost_object = 0
        for obstacle in self.obstacles:
            rightmost_object = max(
                rightmost_object, obstacle.rect.x + obstacle.rect.width)
        for powerup in self.powerups:
            rightmost_object = max(
                rightmost_object, powerup.rect.x + powerup.rect.width)

        # Only spawn if there's enough space
        can_spawn = (rightmost_object < self.WIDTH - self.obstacle_gap)

        if self.spawn_timer >= spawn_rate and can_spawn:
            self.spawn_timer = 0
            spawn_chance = random.random()

            # Obstacle with increasing chance based on difficulty
            if spawn_chance < self.obstacle_chance:
                obstacle_type = random.choice(
                    ["server", "competitor", "regulation", "drone", "laser", "mine"])
                if obstacle_type == "drone":
                    # Spawn a flying drone at a random height
                    self.obstacles.append(FlyingDrone(
                        self.WIDTH, random.randint(100, self.HEIGHT - 150), self.HEIGHT))
                elif obstacle_type == "laser":
                    # Spawn a laser beam at a random height
                    self.obstacles.append(
                        LaserBeam(self.WIDTH, random.randint(100, self.HEIGHT - 150), self.WIDTH))
                else:
                    # Spawn a regular obstacle (server, competitor, regulation)
                    self.obstacles.append(
                        Obstacle(self.WIDTH, self.HEIGHT - 50))

            # Power-ups with decreasing chance based on difficulty
            elif spawn_chance < self.obstacle_chance + 0.2:
                # Decision point: normal power-up or deepfake?
                is_deepfake = random.random() < self.deepfake_chance

                if is_deepfake:
                    # Spawn a deepfake power-up that looks like a bonus but is actually an obstacle
                    height = random.randint(
                        self.HEIGHT - 300, self.HEIGHT - 100)
                    self.powerups.append(DeepfakePowerUp(self.WIDTH, height))
                else:
                    # Regular power-ups as before
                    powerup_type = random.choice(
                        ["jetpack_fuel", "shield", "time_slow", "magnet", "double_points"])
                    if powerup_type == "jetpack_fuel":
                        # Spawn jetpack fuel at a random height
                        height = random.randint(
                            self.HEIGHT - 300, self.HEIGHT - 100)
                        self.powerups.append(JetpackFuel(self.WIDTH, height))
                    elif powerup_type == "shield":
                        # Spawn shield power-up at a random height
                        height = random.randint(
                            self.HEIGHT - 250, self.HEIGHT - 150)
                        self.powerups.append(ShieldPowerUp(self.WIDTH, height))
                    elif powerup_type == "time_slow":
                        # Spawn time slow power-up at a random height
                        height = random.randint(
                            self.HEIGHT - 300, self.HEIGHT - 100)
                        self.powerups.append(
                            TimeSlowPowerUp(self.WIDTH, height))
                    elif powerup_type == "magnet":
                        # Spawn magnet power-up at a random height
                        height = random.randint(
                            self.HEIGHT - 300, self.HEIGHT - 100)
                        self.powerups.append(MagnetPowerUp(self.WIDTH, height))
                    elif powerup_type == "double_points":
                        # Spawn double points power-up at a random height
                        height = random.randint(
                            self.HEIGHT - 300, self.HEIGHT - 100)
                        self.powerups.append(
                            DoublePointsPowerUp(self.WIDTH, height))

    def spawn_decorative_elements(self):
        # Spawn clouds
        self.cloud_spawn_timer += 1
        if self.cloud_spawn_timer >= 120 and self.cloud_image:
            self.cloud_spawn_timer = 0
            cloud_y = random.randint(20, self.HEIGHT // 2 - 50)
            self.clouds.append({
                'x': self.WIDTH,
                'y': cloud_y,
                'speed': random.uniform(0.3, 1.0)
            })

    def update(self):
        if self.game_over:
            self.game_over_delay -= 1
            self.player.load_grave_image()
            return True

        # Update clouds
        for cloud in self.clouds[:]:
            cloud['x'] -= cloud['speed'] * self.game_speed
            if cloud['x'] + self.cloud_image.get_width() < 0:
                self.clouds.remove(cloud)

        # Update trees
        for tree in self.trees[:]:
            # Trees move faster for foreground effect
            tree['x'] -= self.game_speed * 2
            if tree['x'] + self.tree_image.get_width() < 0:
                self.trees.remove(tree)

        # Update background positions (parallax)
        for i in range(len(self.backgrounds)):
            self.bg_positions[i] -= self.backgrounds[i]["speed"] * \
                self.game_speed
            if self.bg_positions[i] <= -self.WIDTH:
                self.bg_positions[i] = 0

        # Update player
        self.player.update()

        # Update the whale
        self.whale.update(self.player.rect.x, self.game_speed)

        # Check collision with whale (game over)
        # if self.player.rect.colliderect(self.whale.rect) and not self.shield_active and not self.player.invincible:
        #     self.game_over = True
        #     if self.sounds["crash"]:
        #         self.sounds["crash"].play()
        #     print(f"Game Over! Score: {self.score}")
        #     return True

        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(self.game_speed)
            if obstacle.rect.right < 0:
                self.obstacles.remove(obstacle)
                self.score += 5  # Points for passing obstacle

            # Collision detection with player hitbox
            player_hitbox = pygame.Rect(
                self.player.rect.x + 5,
                self.player.rect.y + 5,
                self.player.rect.width - 10,
                self.player.rect.height - 10
            )

            if (player_hitbox.colliderect(obstacle.rect) and
                not self.shield_active and
                    not self.player.invincible):
                self.game_over = True
                if self.sounds["crash"]:
                    self.sounds["crash"].play()
                print(f"Game Over! Score: {self.score}")
                return True

        # Update power-ups
        for powerup in self.powerups[:]:
            # Se for um deepfake, passe a posição do jogador para verificar proximidade
            if isinstance(powerup, DeepfakePowerUp):
                powerup.update(self.game_speed, self.player.rect)

                # Se estiver transformando e tiver som de glitch, tocar uma vez
                if powerup.is_transforming and powerup.glitch_timer == powerup.glitch_duration - 1 and self.glitch_sound:
                    self.glitch_sound.play()
            else:
                powerup.update(self.game_speed)

            if powerup.rect.right < 0:
                self.powerups.remove(powerup)

            # Collision detection for power-ups
            if self.player.rect.colliderect(powerup.rect):
                self.powerups.remove(powerup)

                # Verificar se é um deepfake e já se transformou em obstáculo
                if isinstance(powerup, DeepfakePowerUp) and powerup.display_type == "obstacle":
                    # Colisão com um deepfake que se revelou ser um obstáculo
                    if not self.shield_active and not self.player.invincible:
                        self.game_over = True
                        if self.sounds["crash"]:
                            self.sounds["crash"].play()
                        print(
                            f"Game Over! Caught by a deepfake! Score: {self.score}")
                else:
                    # Normal power-up pickup logic
                    if self.sounds["pickup"]:
                        self.sounds["pickup"].play()

                    if isinstance(powerup, JetpackFuel):
                        self.player.add_fuel(powerup.fuel_amount)
                    elif isinstance(powerup, ShieldPowerUp):
                        self.shield_active = True
                        self.shield_timer = powerup.duration * 60  # Convert to frames
                    elif isinstance(powerup, TimeSlowPowerUp):
                        # Slow down game speed
                        self.game_speed = max(2, self.game_speed / 2)
                        self.slow_timer = powerup.duration * 60
                    elif isinstance(powerup, MagnetPowerUp):
                        self.magnet_active = True
                        self.magnet_timer = powerup.duration * 60
                    elif isinstance(powerup, DoublePointsPowerUp):
                        self.double_points_active = True
                        self.double_points_timer = powerup.duration * 60
                    elif isinstance(powerup, InvestmentBonus):
                        self.score += powerup.points

        # Update shield timer
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False

        # Update time slow timer
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.game_speed = self.base_game_speed  # Reset game speed

        # Update magnet timer
        if self.magnet_active:
            self.magnet_timer -= 1
            if self.magnet_timer <= 0:
                self.magnet_active = False

        # Update double points timer
        if self.double_points_active:
            self.double_points_timer -= 1
            if self.double_points_timer <= 0:
                self.double_points_active = False

        # Magnet effect: Attract nearby power-ups
        if self.magnet_active:
            for powerup in self.powerups[:]:
                # Attract within 100px radius
                if powerup.rect.colliderect(self.player.rect.inflate(100, 100)):
                    # Move power-up toward player
                    if powerup.rect.x > self.player.rect.x:
                        powerup.rect.x -= 5
                    else:
                        powerup.rect.x += 5
                    if powerup.rect.y > self.player.rect.y:
                        powerup.rect.y -= 5
                    else:
                        powerup.rect.y += 5

        # Increase distance and score
        self.distance += self.game_speed / 10
        self.score += 0.1  # Small score increment per frame

        # Double points effect
        if self.double_points_active:
            self.score += 0.1  # Additional score increment

        # Check for difficulty milestones
        if self.distance >= self.next_milestone:
            self.increase_difficulty()

        return True

    def increase_difficulty(self):
        self.difficulty_level += 1
        self.next_milestone += 500 * self.difficulty_level

        # Make the game harder
        if self.base_game_speed < self.max_game_speed:
            self.base_game_speed += 0.5
            self.game_speed = self.base_game_speed

        # Increase obstacle chance
        self.obstacle_chance = min(0.7, self.obstacle_chance + 0.05)
        self.deepfake_chance = min(0.15, self.deepfake_chance + 0.02)

        # Reduce obstacle gap for more dense challenges
        self.obstacle_gap = max(200, self.obstacle_gap - 20)

    def draw(self):
        # Draw background with parallax effect
        for i in range(len(self.backgrounds)):
            # Draw background twice for seamless scrolling
            self.screen.blit(
                self.backgrounds[i]["img"], (int(self.bg_positions[i]), 0))
            self.screen.blit(self.backgrounds[i]["img"], (int(
                self.bg_positions[i]) + self.WIDTH, 0))

        # Draw a simple ground
        ground_color = (100, 180, 100)  # Green ground
        pygame.draw.rect(self.screen, ground_color,
                         (0, self.HEIGHT - 50, self.WIDTH, 50))

        # Draw clouds
        if self.cloud_image:
            for cloud in self.clouds:
                self.screen.blit(self.cloud_image,
                                 (int(cloud['x']), cloud['y']))

        # Draw ground
        ground_color = (100, 180, 100)  # Green ground
        pygame.draw.rect(self.screen, ground_color,
                         (0, self.HEIGHT - 50, self.WIDTH, 50))

        # Draw grid lines on ground (sci-fi effect)
        for i in range(0, self.WIDTH, 50):
            x_pos = i - (int(self.distance * 5) % 50)
            pygame.draw.line(self.screen, (120, 200, 120),
                             (x_pos, self.HEIGHT - 50),
                             (x_pos, self.HEIGHT), 1)

        # Draw trees
        if self.tree_image:
            for tree in self.trees:
                self.screen.blit(self.tree_image, (int(tree['x']), tree['y']))

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw the pursuing whale
        self.whale.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw shield effect if active
        if self.shield_active:
            shield_color = (100, 100, 255, 128)  # Blue with transparency
            shield_radius = max(self.player.rect.width,
                                self.player.rect.height) + 5
            shield_surface = pygame.Surface(
                (shield_radius*2, shield_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, shield_color,
                               (shield_radius, shield_radius), shield_radius)
            self.screen.blit(shield_surface,
                             (self.player.rect.centerx - shield_radius,
                              self.player.rect.centery - shield_radius))

        # Draw score and distance
        score_text = self.font.render(
            f"Score: {int(self.score)}", True, (30, 30, 30))
        self.screen.blit(score_text, (10, 10))

        distance_text = self.font.render(
            f"Distance: {int(self.distance)}m", True, (30, 30, 30))
        self.screen.blit(distance_text, (10, 50))

        # Draw jetpack fuel info
        fuel_color = (0, 150, 0)  # Default green
        if self.player.jetpack_fuel < 25:
            fuel_color = (200, 50, 50)  # Red when low
        elif self.player.jetpack_fuel < 50:
            fuel_color = (200, 200, 50)  # Yellow when medium

        fuel_text = self.font.render(
            f"Jetpack: {int(self.player.jetpack_fuel)}%", True, fuel_color)
        self.screen.blit(fuel_text, (10, 90))

        # Draw shield timer if active
        if self.shield_active:
            shield_text = self.small_font.render(
                f"Shield: {self.shield_timer//60 + 1}s", True, (100, 100, 255))
            self.screen.blit(shield_text, (10, 130))

        # Draw dash cooldown if available
        if self.player.can_dash:
            dash_text = self.small_font.render(
                "Dash: Ready", True, (0, 200, 0))
        else:
            dash_text = self.small_font.render(
                f"Dash: {self.player.dash_cooldown//60 + 1}s", True, (150, 150, 150))
        self.screen.blit(dash_text, (10, 160))

        # Draw controls info
        controls_text = [
            {"key": "SPACE", "action": "Jump / Fly Up"},
            {"key": "J", "action": "Toggle Jetpack"},
            {"key": "D", "action": "Dash (temporary invincibility)"}
        ]

        for i, control in enumerate(controls_text):
            control_text = self.small_font.render(
                f"{control['key']}: {control['action']}", True, (30, 30, 30))
            self.screen.blit(control_text, (self.WIDTH - 450, 10 + i * 30))

        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface(
                (self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))

            # Game over text
            game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
            game_over_rect = game_over_text.get_rect(
                center=(self.WIDTH // 2, self.HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, game_over_rect)

            # Final score
            final_score_text = self.font.render(
                f"Final Score: {int(self.score)}", True, (255, 255, 255))
            final_score_rect = final_score_text.get_rect(
                center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(final_score_text, final_score_rect)

            # Restart prompt (only show after delay)
            if self.game_over_delay <= 0:
                restart_text = self.small_font.render(
                    "Press 'R' to restart", True, (255, 255, 255))
                restart_rect = restart_text.get_rect(
                    center=(self.WIDTH // 2, self.HEIGHT // 2 + 50))
                self.screen.blit(restart_text, restart_rect)

        if any(isinstance(p, DeepfakePowerUp) and p.display_type == "obstacle" for p in self.powerups):
            # Text settings
            warning_message = "ALERTA: DEEPFAKE DETECTADO!"
            text_color = (255, 255, 255)  # White text
            bg_color = (200, 0, 0)  # Red background
            
            warning_text = self.font.render(warning_message, True, text_color)
            warning_rect = warning_text.get_rect(center=(self.WIDTH // 2, 50))
            
            # Background behind text
            padding = 10
            bg_rect = pygame.Rect(
                warning_rect.left - padding, 
                warning_rect.top - padding, 
                warning_rect.width + (2 * padding), 
                warning_rect.height + (2 * padding)
            )

            pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=5)  # Red background with rounded corners
            self.screen.blit(warning_text, warning_rect)  # Render text over background

            # Draw indicator for deepfake location
            for powerup in self.powerups:
                if isinstance(powerup, DeepfakePowerUp) and powerup.is_transforming:
                    pygame.draw.line(self.screen, (255, 255, 255),
                                    (self.WIDTH // 2, 80),
                                    (powerup.rect.centerx, powerup.rect.y - 20),
                                    3)
                    pygame.draw.polygon(self.screen, (255, 255, 255), [
                        (powerup.rect.centerx, powerup.rect.y - 25),
                        (powerup.rect.centerx - 10, powerup.rect.y - 40),
                        (powerup.rect.centerx + 10, powerup.rect.y - 40)
                    ])
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            if not self.game_over:
                self.spawn_objects()
                self.spawn_decorative_elements()
            running = self.update() and running
            self.draw()
            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()
