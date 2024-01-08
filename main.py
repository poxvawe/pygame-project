import sys
import pygame
import os

pygame.init()

EVENT_FOR_KETTLE = pygame.USEREVENT + 1
pygame.time.set_timer(EVENT_FOR_KETTLE, 150)

SIZE = WIDTH, HEIGHT = 1920, 1025
HERO_SPEED = 3
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

arena = load_image("new_fon.png")
hero = load_image("hero.jpg", colorkey=-1)
kettle_images = ["0.gif", "1.gif", "2.gif", "3.gif", "4.gif", "5.gif", "6.gif", "7.gif", "8.gif", "9.gif", "10.gif",
                 "11.gif", "12.gif", "13.gif", "14.gif", "15.gif"]

all_sprites = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
allies_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
throne_group = pygame.sprite.Group()
towers_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = hero
        self.now_side = "right"
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.target_pos = None

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

                self.rect.x += move_x
                self.rect.y += move_y
            else:
                self.target_pos = None


class Throne(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y, type):
        super().__init__(throne_group, all_sprites)
        self.image = img
        self.rect = self.image.get_rect().move(pos_x, pos_y)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('zastavka.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    screen.blit(start_button, (WIDTH / 2 - 500, HEIGHT / 2 - 400))
    start_button_rect = start_button.get_rect(topleft=(WIDTH / 2 - 500, HEIGHT / 2 - 400))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    return
        pygame.display.flip()
        clock.tick(FPS)


pygame.display.set_caption("Aota 2")
start_screen()
player = Player(150, 150)
running = True
frame_index = 0
kettles = []
kettle = Throne(load_image(kettle_images[frame_index]), 0, 0, 1)
kettles.append(kettle)

while running:
    screen.fill("white")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                player.update(event)
        if event.type == EVENT_FOR_KETTLE:
            frame_index = (frame_index + 1) % len(kettle_images)
            for sprite in kettles:
                sprite.kill()
            kettles.clear()
            kettle = Throne(load_image(kettle_images[frame_index]), 0, 0, 1)
            kettles.append(kettle)

    all_sprites.update()
    screen.blit(arena, (0, 0))

    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
