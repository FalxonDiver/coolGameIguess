import pygame, sys
from pyvidplayer2 import Video

# Initialize Pygame
pygame.init()

pygame.display.set_caption("Forosophobia")

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPEED = 2
BULLET_SPEED = 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
Back = (103, 184, 57)

#Load Music
pygame.mixer.music.load('music.mp3')
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

#Load Sounds
bullet_sound = pygame.mixer.Sound('bulletShot.mp3')
bullet_sound.set_volume(0.5)

#Load Video
vid = Video('yes.mp4')
vid.set_size((SCREEN_WIDTH, SCREEN_HEIGHT))


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('standing.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.shoot_delay = 150  # milliseconds between shots
        self.last_shot = pygame.time.get_ticks()

    def update(self, keys, bullets):
        if keys[pygame.K_a]:
            self.image = pygame.image.load('left.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            self.image = pygame.image.load('right.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_w]:
            self.image = pygame.image.load('standing.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            self.image = pygame.image.load('standing.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
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

    def shoot(self, bullets, vel_x, vel_y):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.centery, vel_x, vel_y)
            bullets.add(bullet)

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
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('IRS front.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self, player_rect):
        if self.rect.x < player_rect.x:
            self.rect.x += ENEMY_SPEED  # Move right
        elif self.rect.x > player_rect.x:
            self.rect.x -= ENEMY_SPEED  # Move left

        if self.rect.y < player_rect.y:
            self.rect.y += ENEMY_SPEED  # Move down
        elif self.rect.y > player_rect.y:
            self.rect.y -= ENEMY_SPEED  # Move up

# Main function
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    player = Player()
    player_health = 3
    score = 0
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    enemies.add(Enemy(100, 100))

    # Load image for the fence
    fence_image = pygame.image.load('gate.png').convert_alpha()

    # Set the fence image to repeat along the x and y axes
    fence_image = pygame.transform.scale(fence_image, (50, 50))  # Adjust the size as per your image

    running = True
    while running:
        screen.fill(Back)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.update(keys, bullets)
        bullets.update()
        enemies.update(player.rect)  # Pass the player's rect to update the enemy's movement

        # Check for collisions
        player_collisions = pygame.sprite.spritecollide(player, enemies, True)
        if player_collisions:
            # Handle player collision with enemies (e.g., subtract health)
            player_health -= 1  # Subtract health when the player collides with an enemy

        # Check for bullet-enemy collisions
        for bullet in bullets:
            enemy_collisions = pygame.sprite.spritecollide(bullet, enemies, True)
            for enemy in enemy_collisions:
                # Handle enemy destruction (e.g., increase score)
                bullet.kill()
                score += 1  # Increase score when an enemy is destroyed

        # Draw repeating fence image along the edges
        for x in range(0, SCREEN_WIDTH, fence_image.get_width()):
            screen.blit(fence_image, (x, 0))
            screen.blit(fence_image, (x, SCREEN_HEIGHT - fence_image.get_height()))

        for y in range(0, SCREEN_HEIGHT, fence_image.get_height()):
            screen.blit(fence_image, (0, y))
            screen.blit(fence_image, (SCREEN_WIDTH - fence_image.get_width(), y))

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
