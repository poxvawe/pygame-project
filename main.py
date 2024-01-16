import sys
import pygame
import os
import math

pygame.init()

EVENT_FOR_KETTLE = pygame.USEREVENT + 1
EVENT_FOR_DEFAULT_REGENERATION = pygame.USEREVENT + 2
EVENT_FOR_FIREBALL = pygame.USEREVENT + 3
pygame.time.set_timer(EVENT_FOR_KETTLE, 150)
pygame.time.set_timer(EVENT_FOR_DEFAULT_REGENERATION, 1050)
pygame.time.set_timer(EVENT_FOR_FIREBALL, 2100)

SIZE = WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
HERO_SPEED = 3
DEFAULT_REGEN = 1
last_shot_time = pygame.time.get_ticks()
SHOT_COOLDOWN = 2000
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SIZE)
FPS = 50


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


start_button = load_image("letsgo.png")

target_base = load_image("throne.png")
arena = load_image("new_fon.png")
hero = load_image("zxczxc.png")
kettle_images = ["0.gif", "1.gif", "2.gif", "3.gif", "4.gif", "5.gif", "6.gif", "7.gif", "8.gif", "9.gif", "10.gif",
                 "11.gif", "12.gif", "13.gif", "14.gif", "15.gif"]
shot = load_image("purplerocket.png", colorkey=-1)
fireball = load_image("fireball1.png", colorkey=-1)
tower = load_image("tower1.png")

all_sprites = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
allies_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
throne_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = hero
        self.now_side = "right"
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.target_pos = None
        self.damage = 10
        self.health = 30
        self.gun_tip = pygame.math.Vector2(self.rect.x + self.rect.width - 10, self.rect.y + self.rect.height / 2 + 6)

    def update(self, *args, **kwargs):
        if args:
            if args[0].button == 3:
                self.target_pos = args[0].pos
                if self.target_pos[0] < (self.rect.x + self.rect.width / 2) and self.now_side == "right":
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.now_side = "left"
                elif self.target_pos[0] > (self.rect.x + self.rect.width / 2) and self.now_side == "left":
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.now_side = "right"

        if self.target_pos:
            dx = self.target_pos[0] - (self.rect.x + self.rect.width / 2)
            dy = self.target_pos[1] - (self.rect.y + self.rect.height / 2)
            distance = pygame.math.Vector2(dx, dy).length()

            if distance > 5:
                move_x = dx * HERO_SPEED / distance
                move_y = dy * HERO_SPEED / distance

                old_rect = self.rect.copy()

                self.rect.x += move_x
                self.rect.y += move_y
                self.gun_tip.x += move_x
                self.gun_tip.y += move_y

                collide_throne = pygame.sprite.spritecollideany(self, throne_group, collided=pygame.sprite.collide_mask)
                collide_tower = pygame.sprite.spritecollideany(self, tower_group, collided=pygame.sprite.collide_mask)

                if collide_throne or collide_tower:
                    self.rect = old_rect

            else:
                self.target_pos = None

    def change_hp(self, value):
        if self.health + value >= 100:
            self.health = 100
        elif self.health + value < 0:
            self.kill()
            terminate()
        else:
            self.health += value


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, target):
        super().__init__(all_sprites)
        self.image = shot
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.target = target
        self.speed = 8
        self.force = 5

    def update(self, *args, **kwargs):
        if self.target:
            dx = (self.target.rect.x + self.target.rect.width / 2) - self.rect.x
            dy = (self.target.rect.y + self.target.rect.height / 2) - self.rect.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0:
                move_x = dx * self.speed / distance
                move_y = dy * self.speed / distance

                self.rect.x += move_x
                self.rect.y += move_y

            if pygame.sprite.collide_mask(self, self.target):
                if isinstance(self.target, (Throne, Tower)):
                    self.target.take_damage(self.force)
                self.kill()


class Fireball(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, target):
        super().__init__(all_sprites)
        self.image = fireball
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.target = target
        self.speed = 5

    def update(self, *args, **kwargs):
        if self.target:
            dx = self.target.rect.x - self.rect.x
            dy = self.target.rect.y - self.rect.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0:
                move_x = dx * self.speed / distance
                move_y = dy * self.speed / distance

                self.rect.x += move_x
                self.rect.y += move_y

            if pygame.sprite.collide_mask(self, self.target):
                self.target.change_hp(-10)
                self.kill()


class Throne(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y, type):
        super().__init__(throne_group, all_sprites)
        self.image = img
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.type = type
        self.mask = pygame.mask.from_surface(self.image)

        if self.type == "enemy":
            self.health = 20
        else:
            self.health = None

    def take_damage(self, damage):
        if self.health is not None:
            self.health -= damage
            if self.health <= 0:
                self.kill()


class Tower(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y):
        super().__init__(tower_group, all_sprites)
        self.image = img
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.health = 20
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('zastavka.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    screen.blit(start_button, (WIDTH / 2 - start_button.get_rect().x / 8, HEIGHT / 2 + start_button.get_rect().y / 2))
    start_button_rect = start_button.get_rect(
        topleft=(WIDTH / 2 - start_button.get_rect().x / 8, HEIGHT / 2 + start_button.get_rect().y / 2))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    return
        pygame.display.update()
        clock.tick(FPS)


pygame.display.set_caption("Aota 2")
start_screen()
player = Player(150, 150)
tower = Tower(tower, WIDTH / 2 + 170, HEIGHT / 2 - 300)
running = True
frame_index = 0
kettles = []
kettle = Throne(load_image(kettle_images[frame_index]), 0, 0, "friendly")
enemys_throne = Throne(target_base, WIDTH - 326, HEIGHT / 2 - 185, "enemy")
kettles.append(kettle)

while running:
    screen.fill("white")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                player.update(event)
            if event.button == 1:
                distance_to_target = math.sqrt(
                    (player.rect.x - event.pos[0]) ** 2 + (player.rect.y - event.pos[1]) ** 2)
                if distance_to_target <= 700:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_shot_time >= SHOT_COOLDOWN:
                        click_x, click_y = event.pos
                        if tower and tower.health > 0:
                            clicked_sprites = [sprite for sprite in tower_group if
                                               sprite.rect.collidepoint(click_x, click_y)]

                            for clicked_sprite in clicked_sprites:
                                Bullet(player.gun_tip.x, player.gun_tip.y, clicked_sprite)

                            last_shot_time = current_time
                        else:
                            clicked_sprites = [sprite for sprite in throne_group if
                                               sprite.rect.collidepoint(click_x, click_y) and sprite.type == "enemy"]

                            for clicked_sprite in clicked_sprites:
                                Bullet(player.gun_tip.x, player.gun_tip.y, clicked_sprite)

                            last_shot_time = current_time

        if event.type == pygame.KEYDOWN:
            if pygame.key.get_pressed()[pygame.K_x]:
                terminate()
        if event.type == EVENT_FOR_KETTLE:
            frame_index = (frame_index + 1) % len(kettle_images)
            for sprite in kettles:
                sprite.kill()
            kettles.clear()
            kettle = Throne(load_image(kettle_images[frame_index]), 0, 0, 1)
            kettles.append(kettle)
        if event.type == EVENT_FOR_DEFAULT_REGENERATION:
            player.change_hp(DEFAULT_REGEN)
        if event.type == pygame.USEREVENT + 3:
            distance_to_player = math.sqrt(
                (1200 - player.rect.x) ** 2 + (350 - player.rect.y) ** 2)
            if distance_to_player <= 700 and tower.health > 0:
                new_fireball = Fireball(1200, 350, player)

    all_sprites.update()
    screen.blit(arena, (0, 0))

    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
