import sys
import pygame
import os
import math
import random
import sqlite3

pygame.init()

EVENT_FOR_KETTLE = pygame.USEREVENT + 1
EVENT_FOR_DEFAULT_REGENERATION = pygame.USEREVENT + 2
EVENT_FOR_FIREBALL = pygame.USEREVENT + 3
EVENT_FOR_SPAWN_CREEPS = pygame.USEREVENT + 4
EVENT_FOR_SHOT_FROM_CREEPS = pygame.USEREVENT + 5
EVENT_FOR_DEFAULT_BASE_REGENERATION = pygame.USEREVENT + 6
pygame.time.set_timer(EVENT_FOR_KETTLE, 150)
pygame.time.set_timer(EVENT_FOR_DEFAULT_REGENERATION, 1050)
pygame.time.set_timer(EVENT_FOR_FIREBALL, 2100)
pygame.time.set_timer(EVENT_FOR_SPAWN_CREEPS, 6000)
pygame.time.set_timer(EVENT_FOR_SHOT_FROM_CREEPS, 3000)
pygame.time.set_timer(EVENT_FOR_DEFAULT_BASE_REGENERATION, 1050)
spell_costs = [750, 1250, 1100, 550, 1500, 2200, 2800, 2400]

SIZE = WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
DEFAULT_CREEP_SPEED = 3
DEFAULT_HERO_SPEED = 3
DEFAULT_REGEN = 1
DEFAULT_HERO_DAMAGE = 10
MAX_HEALTH = 100
last_shot_time = pygame.time.get_ticks()
DEFAULT_SHOT_COOLDOWN = 2000
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SIZE)
FPS = 50
font = pygame.font.SysFont("comicsansms", 32)


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

target_base = load_image("tron.png")
arena = load_image("new_fon1.png")
hero = load_image("zxczxc.png")
kettle_images = ["0.gif", "1.gif", "2.gif", "3.gif", "4.gif", "5.gif", "6.gif", "7.gif", "8.gif", "9.gif", "10.gif",
                 "11.gif", "12.gif", "13.gif", "14.gif", "15.gif"]
shot = load_image("purplerocket.png", colorkey=-1)
fireball = load_image("fireball1.png", colorkey=-1)
tower = load_image("tower1.png")
creep = load_image("creep.png")
my_ally = load_image("ally.png")

bg_for_spells = load_image("bg_for_spells2.jpg")
spell1 = load_image("angel_rama.png")
spell2 = load_image("bkb.png")
spell3 = load_image("blade.png")
spell4 = load_image("fire_sword_rama.png")
spell5 = load_image("healing_rama.png")
spell6 = load_image("scepter_rama.png")
spell7 = load_image("sf_rama.png")
spell8 = load_image("tornado_speed_rama.png")
money = load_image("cash1.png")
hp_icon = load_image("hp_icon.png")

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
        self.damage = DEFAULT_HERO_DAMAGE
        self.regen = 0
        self.speed = DEFAULT_HERO_SPEED
        self.max_health = MAX_HEALTH
        self.health = self.max_health
        self.coins = 0
        self.gun_tip = [self.rect.x + self.rect.width - 5, self.rect.y + self.rect.height / 2 + 5]
        self.invulnerable = False
        self.invulnerability_duration = 8000
        self.invulnerability_timer = 0
        self.get_coins = 100
        self.cooldown = DEFAULT_SHOT_COOLDOWN

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

            if distance > 3:
                move_x = dx * self.speed / distance
                move_y = dy * self.speed / distance

                old_rect = self.rect.copy()
                gun_old_rect = self.gun_tip.copy()

                self.rect.x += move_x
                self.rect.y += move_y
                self.gun_tip[0] += move_x
                self.gun_tip[1] += move_y

                if self.rect.y > 775:
                    self.rect = old_rect
                    self.gun_tip = gun_old_rect

                collide_throne = pygame.sprite.spritecollideany(self, throne_group, collided=pygame.sprite.collide_mask)
                collide_tower = pygame.sprite.spritecollideany(self, tower_group, collided=pygame.sprite.collide_mask)

                if collide_throne or collide_tower:
                    self.rect = old_rect
                    self.gun_tip = gun_old_rect

            else:
                self.target_pos = None

        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.invulnerability_start_time
            if elapsed_time >= self.invulnerability_duration:
                self.invulnerable = False

    def change_hp(self, value):
        if not self.invulnerable:
            if self.rect.x <= 150 and self.rect.y <= 150:
                value *= 4
                self.farm_coins(-15)
            if self.health + value >= self.max_health:
                self.health = self.max_health
            elif self.health + value < 0:
                self.kill()
                terminate()
            else:
                self.health += value

    def farm_coins(self, value):
        if self.coins + value <= 10000:
            self.coins += value
        else:
            self.coins = 2500


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, target):
        super().__init__(enemies_group, all_sprites)
        self.image = pygame.transform.flip(creep, True, False)
        self.now_side = "right"
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = 10
        self.health = 15
        self.target = target

    def update(self, *args, **kwargs):
        if args:
            if self.target.rect.x < (self.rect.x + self.rect.width / 2) and self.now_side == "right":
                self.image = pygame.transform.flip(self.image, True, False)
                self.now_side = "left"
            elif self.target.rect.x > (self.rect.x + self.rect.width / 2) and self.now_side == "left":
                self.image = pygame.transform.flip(self.image, True, False)
                self.now_side = "right"

        dx = self.target.rect.x - self.rect.x
        dy = self.target.rect.y - self.rect.y
        distance = pygame.math.Vector2(dx, dy).length()

        if distance > 300:
            move_x = dx * DEFAULT_CREEP_SPEED / distance
            move_y = dy * DEFAULT_CREEP_SPEED / distance

            self.rect.x += move_x
            self.rect.y += move_y

    def change_hp(self, value):
        self.health += value
        if self.health <= 0:
            self.kill()
            player.farm_coins(player.get_coins)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, target, type):
        super().__init__(all_sprites)
        self.type = type
        if self.type:
            self.image = shot
        else:
            self.image = fireball
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.target = target
        self.speed = 8
        if self.type:
            self.force = player.damage
        else:
            self.force = enemy.damage

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
            if self.type:
                if pygame.sprite.collide_mask(self, self.target):
                    if isinstance(self.target, (Throne, Tower, Enemy)):
                        self.target.change_hp(-self.force)
                    self.kill()

            else:
                if pygame.sprite.collide_mask(self, self.target):
                    self.target.change_hp(-self.force)
                    self.kill()


class Throne(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y, type):
        super().__init__(throne_group, all_sprites)
        self.image = img
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.type = type
        self.mask = pygame.mask.from_surface(self.image)

        if self.type == "enemy":
            self.max_health = 200
            self.health = self.max_health
        else:
            self.health = None

    def change_hp(self, value):
        if self.health:
            if self.health + value <= self.max_health:
                self.health += value
            else:
                self.health = self.max_health
            if self.health <= 0:
                self.kill()
                terminate()


class Tower(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y):
        super().__init__(tower_group, enemies_group, all_sprites)
        self.image = img
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.max_health = 100
        self.health = self.max_health
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = 20

    def change_hp(self, value):
        if self.health + value <= self.max_health:
            self.health += value
        else:
            self.health = self.max_health
        if self.health <= 0:
            self.kill()
            player.farm_coins(1500)


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
enemies_throne = Throne(target_base, WIDTH - 400, HEIGHT / 2 - 195, "enemy")
kettles.append(kettle)

while running:
    hp = font.render(f"{player.health} / {player.max_health}", 1, (255, 0, 0))
    coins = font.render(f"{player.coins}", 1, (255, 215, 0))
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
                if distance_to_target <= 510:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_shot_time >= player.cooldown:
                        click_x, click_y = event.pos
                        if tower and tower.health > 0:
                            clicked_sprites = [sprite for sprite in enemies_group if
                                               sprite.rect.collidepoint(click_x, click_y)]

                            for clicked_sprite in clicked_sprites:
                                Bullet(player.rect.x + player.rect.width - 5, player.rect.height / 2 + 5,
                                       clicked_sprite, 1)

                            last_shot_time = current_time
                        else:
                            clicked_sprites = [sprite for sprite in throne_group if
                                               sprite.rect.collidepoint(click_x, click_y) and sprite.type == "enemy"]
                            clicked_sprites += [sprite for sprite in enemies_group if
                                                sprite.rect.collidepoint(click_x, click_y)]

                            for clicked_sprite in clicked_sprites:
                                Bullet(player.rect.x + player.rect.width - 5, player.rect.height / 2 + 5,
                                       clicked_sprite, 1)

                            last_shot_time = current_time
                if 10 <= event.pos[0] <= 10 + spell1.get_width() and 930 <= event.pos[
                    1] <= 930 + spell1.get_height() and player.coins >= 750:
                    player.max_health += 50
                    player.speed += 1
                    player.coins -= 750
                if 170 <= event.pos[0] <= 170 + spell2.get_width() and 930 <= event.pos[
                    1] <= 930 + spell2.get_height() and player.coins >= 1250:
                    player.invulnerable = True
                    player.invulnerability_start_time = pygame.time.get_ticks()
                    player.coins -= 1250
                if 330 <= event.pos[0] <= 330 + spell3.get_width() and 930 <= event.pos[
                    1] <= 930 + spell3.get_height() and player.coins >= 1100:
                    player.damage += 10
                    player.coins -= 1100
                if 490 <= event.pos[0] <= 490 + spell4.get_width() and 930 <= event.pos[
                    1] <= 930 + spell4.get_height() and player.coins >= 550:
                    player.get_coins += 25
                    player.coins -= 550
                if 650 <= event.pos[0] <= 650 + spell5.get_width() and 930 <= event.pos[
                    1] <= 930 + spell5.get_height() and player.coins >= 1500:
                    player.health += player.max_health // 2
                    player.coins -= 1500
                if 810 <= event.pos[0] <= 810 + spell6.get_width() and 930 <= event.pos[
                    1] <= 930 + spell6.get_height() and player.coins >= 2200:
                    player.damage += 5
                    player.speed += 3
                    player.max_health += 75
                    player.health += 25
                    player.get_coins += 15
                    player.coins -= 2200
                if 970 <= event.pos[0] <= 970 + spell7.get_width() and 930 <= event.pos[
                    1] <= 930 + spell7.get_height() and player.coins >= 2800:
                    player.max_health += 150
                    player.health += 150
                    player.coins -= 2800
                if 1130 <= event.pos[0] <= 1130 + spell8.get_width() and 930 <= event.pos[
                    1] <= 930 + spell8.get_height() and player.coins >= 2450:
                    player.cooldown -= 1000
                    player.coins -= 2450

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
            player.change_hp(DEFAULT_REGEN + player.regen)
        if event.type == EVENT_FOR_DEFAULT_BASE_REGENERATION:
            tower.change_hp(1)
            enemies_throne.change_hp(1)
        if event.type == EVENT_FOR_SHOT_FROM_CREEPS:
            for enemy in enemies_group:
                distance_to_player = math.sqrt(
                    (enemy.rect.x - player.rect.x) ** 2 + (enemy.rect.y - player.rect.y) ** 2)
                if distance_to_player <= 500 and enemy.health > 0:
                    shot_from_enemy = Bullet(enemy.rect.x, enemy.rect.y, player, 0)
        if event.type == EVENT_FOR_SPAWN_CREEPS:
            enemy = Enemy(WIDTH - 200, random.randint(0, 900), player)

    all_sprites.update()
    screen.blit(arena, (0, 0))
    screen.blit(bg_for_spells, (0, 900))
    screen.blit(spell1, (10, 930))
    screen.blit(spell2, (170, 930))
    screen.blit(spell3, (330, 930))
    screen.blit(spell4, (490, 930))
    screen.blit(spell5, (650, 930))
    screen.blit(spell6, (810, 930))
    screen.blit(spell7, (970, 930))
    screen.blit(spell8, (1130, 930))
    screen.blit(hp_icon, (1610, 910))
    screen.blit(hp, (1700, 910))
    screen.blit(money, (1606, 980))
    screen.blit(coins, (1700, 980))

    for i in range(len(spell_costs)):
        cost = font.render(f"{spell_costs[i]}", 1, (255, 215, 10))
        screen.blit(cost, (15 + i * 160, 1040))

    for enemy in enemies_group:
        enemy_hp = font.render(f"{enemy.health}", 1, (255, 0, 0))
        screen.blit(enemy_hp, (enemy.rect.x - 5, enemy.rect.y - 15))

    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
