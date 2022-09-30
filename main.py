import pygame, sys
from pygame.locals import *
from random import randint, choice


# noinspection PyTypeChecker
class SpaceShip(pygame.sprite.Sprite):

    def __init__(self, groups, health):
        super().__init__(groups)
        self.image = pygame.image.load("./graphics/spaceship.png").convert_alpha()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.mask = pygame.mask.from_surface(self.image)
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.laser_sound = pygame.mixer.Sound('./sound/laser.wav')
        self.laser_sound.set_volume(0.1)
        self.explosion_sound = pygame.mixer.Sound('./sound/explosion.wav')
        self.explosion_sound.set_volume(0.1)
        self.explosion2_sound = pygame.mixer.Sound('./sound/explosion2.wav')
        self.explosion2_sound.set_volume(0.1)
        self.game_over = 0  # 0: game on, 1: player won, 2: player lost

    def draw_health_make_sound(self):
        health_ratio = self.health_remaining / self.health_start
        pygame.draw.rect(screen, RED, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, GREEN,
                             (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * health_ratio), 15))
        else:
            print("Game Over")
            self.game_over = -1
            self.explosion2_sound.play()
            explosion = Explosion(self.rect.center, 3, explosions_group)
            self.kill()

    def bullet_collision(self):
        if pygame.sprite.groupcollide(spaceship_group, alien_bullets_group, False, True, pygame.sprite.collide_mask):
            self.health_remaining -= 1
            explosion = Explosion(self.rect.center, 1, explosions_group)
            self.explosion_sound.play()

    def update(self):
        self.bullet_collision()
        self.draw_health_make_sound()
        # set movement speed
        speed = 8
        # cooldown
        cooldown = 250  # miliseconds
        # time now
        time_now = pygame.time.get_ticks()

        # get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += speed
        if key[pygame.K_SPACE] and (time_now - self.last_shot > cooldown):
            bullet = Bullet(self.rect.midtop, bullets_group)
            self.last_shot = time_now
            self.laser_sound.play()


# noinspection PyTypeChecker
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load("./graphics/bullet.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.explosion_sound = pygame.mixer.Sound('./sound/explosion.wav')
        self.explosion_sound.set_volume(0.1)

    def bullet_collision(self):
        if pygame.sprite.groupcollide(aliens_group, bullets_group, True, True, pygame.sprite.collide_mask):
            explosion = Explosion(self.rect.center, 2, explosions_group)
            self.explosion_sound.play()

    def update(self):
        self.bullet_collision()
        self.rect.y -= 5

        if self.rect.bottom < 0:
            self.kill()


# noinspection PyTypeChecker
class Alien(pygame.sprite.Sprite):
    def __init__(self, pos: object, groups: object) -> object:
        super().__init__(groups)
        self.image = pygame.image.load(f"./graphics/alien{randint(1, 5)}.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = 1
        self.counter = 0

    def update(self):
        self.rect.x += self.direction
        self.counter += 1

        if abs(self.counter) > 75:
            self.direction *= -1
            self.counter *= self.direction


# noinspection PyTypeChecker
class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load("./graphics/alien_bullet.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.explosion_sound = pygame.mixer.Sound('./sound/explosion.wav')
        self.explosion_sound.set_volume(0.1)

    def bullet_collision(self):
        if pygame.sprite.groupcollide(alien_bullets_group, bullets_group, True, True, pygame.sprite.collide_mask):
            print("bullet collision")

    def update(self):
        self.bullet_collision()

        self.rect.y += 2

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(groups)
        self.images = []
        self.index = 0

        for i in range(1, 6):
            img = pygame.image.load(f"./graphics/exp{i}.png").convert_alpha()
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            self.images.append(img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # update explosion animation
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]
        # when the animation is complete delete explosion
        if self.index >= len(self.images) - 1 and self.counter > explosion_speed:
            self.kill()


def draw_text(text, font, text_col, pos):
    img = font.render(text, True, text_col)
    screen.blit(img, pos)


def draw_bg():
    screen.blit(bg_surf, (0, 0))


def create_aliens():
    for row in range(ROWS):
        for item in range(COLS):
            alien = Alien((100 + item * 100, 100 + row * 70), aliens_group)


pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
RED = (255, 0, 0)
GREEN = (0, 255, 0)
FPS = 60
ROWS = 5
COLS = 5

clock = pygame.time.Clock()
last_alien_shot = pygame.time.get_ticks()
alien_bullet_cooldown = 1000  # ms

font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)
white = (255, 255, 255)
countdown = 3
last_count = pygame.time.get_ticks()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Space Invaders')

# load images
## background image
bg_surf = pygame.image.load("./graphics/bg.png").convert_alpha()

## sprite groups
spaceship_group = pygame.sprite.GroupSingle()
bullets_group = pygame.sprite.Group()
aliens_group = pygame.sprite.Group()
alien_bullets_group = pygame.sprite.Group()
explosions_group = pygame.sprite.Group()
spaceship = SpaceShip(spaceship_group, 3)
create_aliens()

run = True
while run:

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()

    clock.tick(FPS)
    draw_bg()
    if countdown == 0:
        # update
        time_now = pygame.time.get_ticks()
        if time_now - last_alien_shot > alien_bullet_cooldown and len(alien_bullets_group) < 5 and len(
                aliens_group) > 0:
            attacking_alien = choice(aliens_group.sprites())
            alien_bullet = AlienBullet(attacking_alien.rect.midbottom, alien_bullets_group)
            last_alien_shot = time_now
        if len(aliens_group) == 0:
            game_over = 1  # player won

        if spaceship.game_over == 0:
            spaceship_group.update()
            bullets_group.update()
            aliens_group.update()
            alien_bullets_group.update()
        elif spaceship.game_over == -1:
            draw_text("GAME OVER!", font40, white, pos1)
        elif spaceship.game_over == 1:
            draw_text("YOU WON!", font40, white, pos1)


    if countdown > 0:
        pos1 = (int(SCREEN_WIDTH / 2 - 110), int(SCREEN_HEIGHT / 2 + 50))
        pos2 = (int(SCREEN_WIDTH / 2 - 10), int(SCREEN_HEIGHT / 2 + 100))
        draw_text("GET READY!", font40, white, pos1)
        draw_text(f'{countdown}', font30, white, pos2)
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer
    explosions_group.update()

    # draw sprites
    spaceship_group.draw(screen)
    bullets_group.draw(screen)
    aliens_group.draw(screen)
    alien_bullets_group.draw(screen)

    explosions_group.draw(screen)

    # display update

    pygame.display.update()

pygame.quit()
