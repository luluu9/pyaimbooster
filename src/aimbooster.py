import pygame
import pygame.freetype
import random
import time
from pygame.constants import USEREVENT


from pygame.locals import (
    QUIT,
)

pygame.init()
pygame.display.set_caption('aimbooster v.0.0.1')

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

TARGET_SPAWNRATE = 2 # targets per second 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

ADD_TARGET = USEREVENT + 1
pygame.time.set_timer(ADD_TARGET, int(1000/TARGET_SPAWNRATE))

scoreCounter = None


class ScoreCounter():
    def __init__(self):
        self.hits = 0
        self.all_targets = 0
        self.font_size = 30
        self.font = pygame.freetype.SysFont("CourierNew", self.font_size)
        self.color = (255, 255, 255)
        self.shoots = 0
        self.start_time = time.time()
    
    def update(self):
        text = f"{self.hits}/{self.all_targets}"
        text_rect = self.font.get_rect(text, size=30) 
        text_rect.midtop = screen.get_rect().midtop
        self.font.render_to(screen, text_rect, text, self.color)

    def add_hit(self):
        self.hits += 1
    
    def add_target(self):
        self.all_targets += 1

    def add_shoot(self):
        self.shoots += 1
    
    # return how much time current round takes
    def get_time(self):
        return time.time() - self.start_time
    

class Target():
    def __init__(self):
        self.color = get_random_color()
        self.max_radius = 50
        self.reached_max = False
        self.pos = get_random_pos(self.max_radius)
        self.radius = 0
        self.rect = None

    def update(self):
        if self.radius < self.max_radius and not self.reached_max:
            self.radius += 1
        else:
            self.reached_max = True
            self.radius -= 1
            # destroy this object if smaller than 1px
            if self.radius <= 0:
                self.destroy()
        self.rect = pygame.draw.circle(screen, self.color, self.pos, self.radius)

    def check_collision(self, mouse_pos):
        if pow((mouse_pos[0] - self.pos[0]), 2) + pow((mouse_pos[1] - self.pos[1]), 2) <= pow(self.radius, 2):
            scoreCounter.add_hit()
            self.destroy()

    def destroy(self):
        targets_to_delete.append(self)
        scoreCounter.add_target()


def get_random_pos(margin=0):
    x = random.randint(margin, SCREEN_WIDTH-margin)
    y = random.randint(margin, SCREEN_HEIGHT-margin)
    return (x, y)


def get_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)


scoreCounter = ScoreCounter()

targets = [Target()]
targets_to_delete = []

running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            for target in targets:
                target.check_collision(pygame.mouse.get_pos())
            scoreCounter.add_shoot()
        elif event.type == QUIT:
            running = False
        elif event.type == ADD_TARGET:
            targets.append(Target())
            
    # update targets size
    for target in targets:
        target.update()
    
    # delete unused targets
    while len(targets_to_delete) > 0:
        targets.remove(targets_to_delete.pop())
    
    # update counter
    scoreCounter.update()

    # refresh display
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()


# todo
# - add training modes
# - create summary of training based on stats
# - forbid to spawn new target onto other target
