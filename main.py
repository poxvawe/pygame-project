import sys
import pygame
import os

pygame.init()

EVENT_FOR_KETTLE = pygame.USEREVENT + 1
pygame.time.set_timer(EVENT_FOR_KETTLE, 150)

SIZE = WIDTH, HEIGHT = 1500, 900
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
    def __init__(self, img, pos_x, pos_y):
        super().__init__(throne_group, all_sprites)
        self.image = img
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.move_camera = False

    def apply(self, target):
        return target.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + WIDTH // 2
        y = -target.rect.y + HEIGHT // 2

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH), x)
        y = max(-(self.height - HEIGHT), y)

        if target.rect.x < WIDTH / 2 - 200 or target.rect.x > self.width - WIDTH / 2 + 200 \
                or target.rect.y < HEIGHT / 2 - 200 or target.rect.y > self.height - HEIGHT / 2 + 200:
            self.move_camera = True
        else:
            self.move_camera = False

        if self.move_camera:
            self.camera = pygame.Rect(x, y, self.width, self.height)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('zastavka.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


pygame.display.set_caption("Aota 2")
start_screen()
player = Player(150, 150)
camera = Camera(WIDTH, HEIGHT)
running = True
frame_index = 0
kettles = []
kettle = Throne(load_image(kettle_images[frame_index]), 0, 0)
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
            kettle = Throne(load_image(kettle_images[frame_index]), 0, 0)
            kettles.append(kettle)

    all_sprites.update()
    screen.blit(arena, (0, 0))

    camera.update(player)
    for sprite in all_sprites:
        if camera.move_camera:
            sprite_rect = sprite.rect.move(camera.camera.topleft)
            screen.blit(sprite.image, sprite_rect)
        else:
            screen.blit(sprite.image, sprite.rect)

    pygame.display.flip()
    print(player.rect.x, player.rect.y)
    clock.tick(FPS)

pygame.quit()
sys.exit()
