import pygame
import pygame.freetype
import random
import time
from pygame.constants import USEREVENT

from pygame.locals import (
    QUIT,
)


class ScoreCounter():
    def __init__(self):
        self.hits = 0
        self.all_targets = 0
        self.font_size = 30
        self.font = pygame.freetype.SysFont("CourierNew", self.font_size)
        self.shoots = 0
        self.start_time = time.time()
    
    def update(self):
        text = f"{self.hits}/{self.all_targets}"
        text_rect = self.font.get_rect(text, size=30) 
        text_rect.midtop = screen.get_rect().midtop
        self.font.render_to(screen, text_rect, text, score_color)

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
        self.max_radius = 50
        self.reached_max = False
        self.pos = self.get_random_pos(self.max_radius)
        self.radius = 0
        self.outline_margin = 4

    def update(self):
        if self.radius < self.max_radius and not self.reached_max:
            self.radius += 1
        else:
            self.reached_max = True
            self.radius -= 1
            # destroy this object if smaller than 1px
            if self.radius <= 0:
                self.destroy()
        # draw outline
        pygame.draw.circle(screen, outline_color, self.pos, self.radius, self.outline_margin)
        # draw filling
        pygame.draw.circle(screen, filling_color, self.pos, self.radius-self.outline_margin)

    def check_collision(self, mouse_pos):
        if pow((mouse_pos[0] - self.pos[0]), 2) + pow((mouse_pos[1] - self.pos[1]), 2) <= pow(self.radius, 2):
            scoreCounter.add_hit()
            self.destroy()

    def destroy(self):
        targets_to_delete.append(self)
        scoreCounter.add_target()
    
    def get_random_pos(self, margin=0):
        x = random.randint(margin, SCREEN_WIDTH-margin)
        y = random.randint(margin, SCREEN_HEIGHT-margin)
        return (x, y)


class Game():
    def __init__(self):
        self.change_game_mode("lobby")

    def change_game_mode(self, game_mode):
        if game_mode == "lobby":
            self.load_lobby()
        elif game_mode == "arcade":
            self.load_arcade()
        else:
            raise Exception("There is no provided game mode: " + str(game_mode))
        self.game_mode = game_mode
    
    def load_lobby(self):
        pass

    def load_arcade(self):
        global scoreCounter, targets, targets_to_delete
        scoreCounter = ScoreCounter()
        targets = [Target()]
        targets_to_delete = []
        pygame.time.set_timer(ADD_TARGET, int(1000/TARGET_SPAWNRATE))
    
    def frame(self):
        if self.game_mode == "lobby":
            self.lobby_frame()
        elif self.game_mode == "arcade":
            self.arcade_frame()
    
    def lobby_frame(self):
        pass

    def arcade_frame(self):
        screen.fill(background_color)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for target in targets:
                    target.check_collision(pygame.mouse.get_pos())
                scoreCounter.add_shoot()
            elif event.type == ADD_TARGET:
                targets.append(Target())
                
        # update targets size
        for target in targets:
            target.update()
        
        # delete unused targets
        while len(targets_to_delete) > 0:
            try:
                targets.remove(targets_to_delete.pop())
            except ValueError: # probably double clicked faster than delta time
                pass 
        # update counter
        scoreCounter.update()


# BASE SETTINGS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# PYGAME INIT
pygame.init()
pygame.display.set_caption('aimbooster v.0.0.1')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# APPEARANCE 
background_color = (222, 222, 222)
outline_color = (0, 0, 0) 
filling_color = (255, 255, 255)
score_color = (74, 74, 74)

# GAME MECHANICS
scoreCounter = None
targets = []
targets_to_delete = []
TARGET_SPAWNRATE = 3 # targets per second 

# GAME EVENTS
ADD_TARGET = USEREVENT + 1

# LOAD GAME
game = Game()
game.change_game_mode("arcade")

# MAINLOOP
running = True
while running:
    for event in pygame.event.get(QUIT):
        if event.type == QUIT:
            running = False
    game.frame()
    # refresh display
    pygame.display.update()
    clock.tick(FPS)
pygame.quit()


# todo
# - add training modes
# - create summary of training based on stats
# - forbid to spawn new target onto other target
