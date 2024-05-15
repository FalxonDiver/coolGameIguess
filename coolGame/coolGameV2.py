import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

pygame.display.set_caption("Forosophobia")

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPEED = 2
BULLET_SPEED = 8
INVINCIBILITY_DURATION = 2000
Pxsize = 50
Pysize = 50
Exsize = 40
Eysize= 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND = (101, 184, 104)

# Load Music
pygame.mixer.music.load('music.mp3')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

# Load Sounds
bullet_sound = pygame.mixer.Sound('bulletShot.mp3')
bullet_sound.set_volume(0.5)
hit = pygame.mixer.Sound('hit.mp3')
hit.set_volume(0.5)
die = pygame.mixer.Sound('death.mp3')
die.set_volume(0.4)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('standing.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (Pxsize, Pysize))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.shoot_delay = 150  # milliseconds between shots
        self.last_shot = pygame.time.get_ticks()
        self.last_hit = pygame.time.get_ticks()
        self.invincible = False

    def update(self, keys, bullets):
        if keys[pygame.K_a]:
            self.image = pygame.image.load('left.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (Pxsize, Pysize))
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            self.image = pygame.image.load('right.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (Pxsize, Pysize))
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_w]:
            self.image = pygame.image.load('back.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (Pxsize, Pysize))
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            self.image = pygame.image.load('standing.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (Pxsize, Pysize))
            self.rect.y += PLAYER_SPEED
        if keys[pygame.K_UP]:  # Shooting with arrow keys
            if keys[pygame.K_RIGHT]:
                self.shoot(bullets, 1, -1)
            if keys[pygame.K_LEFT]:
                self.shoot(bullets, -1, -1)
            self.shoot(bullets, 0, -1)  # Shoot up
        if keys[pygame.K_DOWN]:
            if keys[pygame.K_RIGHT]:
                self.shoot(bullets, 1, 1)
            if keys[pygame.K_LEFT]:
                self.shoot(bullets, -1, 1)
            self.shoot(bullets, 0, 1)  # Shoot down
        if keys[pygame.K_LEFT]:
            self.shoot(bullets, -1, 0)  # Shoot left
        if keys[pygame.K_RIGHT]:
            self.shoot(bullets, 1, 0)  # Shoot right

        # Update invincibility state
        now = pygame.time.get_ticks()
        if self.invincible and now - self.last_hit > INVINCIBILITY_DURATION:
            self.invincible = False

    def shoot(self, bullets, vel_x, vel_y):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.centery, vel_x, vel_y)
            bullets.add(bullet)

    def take_damage(self):
        now = pygame.time.get_ticks()
        if not self.invincible:
            self.invincible = True
            self.last_hit = now
            return True
        return False


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vel_x, vel_y):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = vel_x * BULLET_SPEED
        self.vel_y = vel_y * BULLET_SPEED
        bullet_sound.play()

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self.image = pygame.image.load('IRS1F.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (Exsize, Eysize))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = health

    def update(self, player_rect, all_enemies):
        enemyImageF= "IRS" + str(self.health) + "F.png"
        enemyImageB = "IRS" + str(self.health) + "B.png"

        # Move towards the player
        if self.rect.x < player_rect.x:
            self.rect.x += ENEMY_SPEED  # Move right
        elif self.rect.x > player_rect.x:
            self.rect.x -= ENEMY_SPEED  # Move left

        if self.rect.y < player_rect.y:
            self.rect.y += ENEMY_SPEED  # Move down
            self.image = pygame.image.load(enemyImageF).convert_alpha()
            self.image = pygame.transform.scale(self.image, (Exsize, Eysize))
        elif self.rect.y > player_rect.y:
            self.rect.y -= ENEMY_SPEED  # Move up
            self.image = pygame.image.load(enemyImageB).convert_alpha()
            self.image = pygame.transform.scale(self.image, (Exsize, Eysize))

        # Collision avoidance
        for other_enemy in all_enemies:
            if other_enemy == self:
                continue
            if self.rect.colliderect(other_enemy.rect):
                # Calculate a repulsive force
                dx = self.rect.x - other_enemy.rect.x
                dy = self.rect.y - other_enemy.rect.y
                distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)  # Avoid division by zero
                repulsion_strength = 2  # The strength of the repulsive force
                self.rect.x += int(repulsion_strength * dx / distance)
                self.rect.y += int(repulsion_strength * dy / distance)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()


# Main function
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Player()
    player_health = 3
    score = 0
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    ENEMY_WAVE_INCREMENT = 1
    ENEMY_WAVE_SIZE = 5
    wave_countdown = ENEMY_WAVE_SIZE

    # Load image for the fence
    fence_image = pygame.image.load('gate.png').convert_alpha()

    # Set the fence image to repeat along the x and y axes
    fence_image = pygame.transform.scale(fence_image, (50, 50))  # Adjust the size as per your image

    running = True
    while running:
        screen.fill(BACKGROUND)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.update(keys, bullets)
        bullets.update()

        # Update enemies and check for collisions with other enemies
        enemies.update(player.rect, enemies)

        # Check for collisions
        player_collisions = pygame.sprite.spritecollide(player, enemies, False)
        if player_collisions:
            # Handle player collision with enemies (e.g., subtract health)
            if player.take_damage():
                player_health -= 1  # Subtract health when the player collides with an enemy
                hit.play()
                print(player_health)

        # Check for bullet-enemy collisions
        for bullet in bullets:
            enemy_collisions = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in enemy_collisions:
                # Handle enemy taking damage
                bullet.kill()
                enemy.take_damage()
                if enemy.health <= 0:
                    score += 1  # Increase score when an enemy is destroyedd
        
        # Spawn enemies
        if not enemies and wave_countdown <= 0:
            wave_countdown = ENEMY_WAVE_SIZE
            for _ in range(ENEMY_WAVE_SIZE):
                while True:
                    x = random.randint(0, SCREEN_WIDTH - 50)
                    Ty = random.randint(-150, -100)  # Ensure enemies start off-screen
                    By = random.randint(700, 850)
                    randY = random.randint(0, 2)
                    if randY == 0:
                        y = Ty
                        health = random.choice([1, 2,])
                        new_enemy = Enemy(x, y, health)
                    else:
                        y = By
                        health = random.choice([1, 2,])
                        new_enemy = Enemy(x, y, health)
                    if not pygame.sprite.spritecollide(new_enemy, enemies, False):
                        enemies.add(new_enemy)  
                        break
            print("Next Round Start!")
            print("Spawned " + str(ENEMY_WAVE_SIZE) + " Enemies")
            ENEMY_WAVE_SIZE += ENEMY_WAVE_INCREMENT
        
        wave_countdown -= 1

        if player_health == 0:
            die.play()
            time.sleep(0.2)
            print("Player Died")
            pygame.quit()
            sys.exit()
        
        # Draw repeating fence image along the edges
        for x in range(0, SCREEN_WIDTH, fence_image.get_width()):
            screen.blit(fence_image, (x, 0))
            screen.blit(fence_image, (x, SCREEN_HEIGHT - fence_image.get_height()))

        # Draw sprites
        enemies.draw(screen)
        bullets.draw(screen)
        screen.blit(player.image, player.rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()