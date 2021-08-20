import pygame
import random
from pygame.constants import USEREVENT

from pygame.locals import (
    QUIT,
)

pygame.init()
pygame.display.set_caption('aimbooster v.0.0.1')

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

TARGET_SPAWNRATE = 3 # targets per second 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

ADD_TARGET = USEREVENT + 1
pygame.time.set_timer(ADD_TARGET, 1000//TARGET_SPAWNRATE)


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
        if self.rect: # if instanced in same frame as click a rect is None
            if self.rect.collidepoint(mouse_pos):
                self.destroy()
    
    def destroy(self):
        targets_to_delete.append(self)


def get_random_pos(margin=0):
    return [random.randint(margin, SCREEN_WIDTH-margin), random.randint(margin, SCREEN_HEIGHT-margin)]


def get_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)


targets = [Target()]
targets_to_delete = []

running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            for target in targets:
                target.check_collision(pygame.mouse.get_pos())
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

    # refresh display
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()


# todo
# - forbid to spawn new target onto other target
# - count hits
