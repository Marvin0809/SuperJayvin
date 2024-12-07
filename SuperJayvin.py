import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SuperJayvin")

player_image = pygame.image.load("player.png")
fireball_image = pygame.image.load("fireball.png")
bullet_image = pygame.image.load("bullet.png")
smoke_image = pygame.image.load("smoke.png")

player_image = pygame.transform.scale(player_image, (50, 50))
fireball_image = pygame.transform.scale(fireball_image, (30, 30))
bullet_image = pygame.transform.scale(bullet_image, (30, 30))
smoke_image = pygame.transform.scale(smoke_image, (30, 30))

font = pygame.font.SysFont("Arial", 24)

# Define the score thresholds to reach each level
score_to_next_level = [10, 20, 40]  # Example levels' thresholds (can be adjusted)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed = 8
        self.boosted_speed = 12
        self.is_boosted = False
        self.boost_time = 0

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and not self.is_boosted:
            self.is_boosted = True
            self.boost_time = pygame.time.get_ticks()

        if self.is_boosted and pygame.time.get_ticks() - self.boost_time > 2000:
            self.is_boosted = False

        current_speed = self.boosted_speed if self.is_boosted else self.speed

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= current_speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += current_speed

class Fireball(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = fireball_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 30)
        self.rect.y = -30
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.y = -30
            self.rect.x = random.randint(0, SCREEN_WIDTH - 30)

class Smoke(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = smoke_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.life_time = 500
        self.start_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.start_time > self.life_time:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

def create_game_objects():
    global player, fireballs, bullets, smokes, all_sprites, score, level, fireball_speed, fireball_count
    player = Player()
    fireballs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    smokes = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    all_sprites.add(player)
    
    score = 0
    level = 1
    fireball_speed = 2
    fireball_count = 2

    create_fireballs()

def create_fireballs():
    for _ in range(fireball_count):
        fireball = Fireball(fireball_speed)
        fireballs.add(fireball)
        all_sprites.add(fireball)

def display_level_complete_message():
    level_complete_text = font.render("Level Complete!", True, BLACK)
    screen.blit(level_complete_text, (SCREEN_WIDTH // 2 - level_complete_text.get_width() // 2, SCREEN_HEIGHT // 2))

def display_game_over_screen():
    game_over_text = font.render("Game Over!", True, BLACK)
    replay_text = font.render("Replay", True, BLACK)
    exit_text = font.render("Exit", True, BLACK)
    
    screen.fill(WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 4))
    
    # Buttons
    replay_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
    exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
    
    pygame.draw.rect(screen, BLACK, replay_button, 2)
    pygame.draw.rect(screen, BLACK, exit_button, 2)
    
    screen.blit(replay_text, (SCREEN_WIDTH // 2 - replay_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
    screen.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

    pygame.display.flip()

    return replay_button, exit_button

running = True
clock = pygame.time.Clock()
create_game_objects()

# Initialize level_complete_message_displayed
level_complete_message_displayed = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and not level_complete_message_displayed:
            if event.key == pygame.K_z:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                bullets.add(bullet)
                all_sprites.add(bullet)

    if not level_complete_message_displayed:
        all_sprites.update()

        for bullet in bullets:
            collided_fireballs = pygame.sprite.spritecollide(bullet, fireballs, False)
            for fireball in collided_fireballs:
                score += 1
                bullet.kill()

                smoke = Smoke(fireball.rect.centerx, fireball.rect.centery)
                smokes.add(smoke)
                all_sprites.add(smoke)

                fireball.rect.y = -30
                fireball.rect.x = random.randint(0, SCREEN_WIDTH - 30)

        if pygame.sprite.spritecollide(player, fireballs, False):
            print("Game Over!")
            replay_button, exit_button = display_game_over_screen()

            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting_for_input = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        if replay_button.collidepoint(mouse_x, mouse_y):
                            create_game_objects()
                            waiting_for_input = False
                        elif exit_button.collidepoint(mouse_x, mouse_y):
                            running = False
                            waiting_for_input = False

            continue

        for fireball in fireballs:
            fireball.update()

        if score >= score_to_next_level[level - 1]:
            level += 1
            if level <= 3:
                fireball_speed += 2
                fireball_count += 2
                create_fireballs()

        if level == 4 and not level_complete_message_displayed:
            display_level_complete_message()
            level_complete_message_displayed = True

        screen.fill(WHITE)
        all_sprites.draw(screen)

        score_text = font.render(f"Score: {score}", True, BLACK)
        level_text = font.render(f"Level: {level - 1}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
sys.exit()
