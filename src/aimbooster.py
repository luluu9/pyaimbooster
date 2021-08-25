import pygame
import pygame.freetype
import random
import time
import gamemodes
from pygame.constants import USEREVENT
from appearance import (default_font, score_color, outline_color, filling_color)

from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_s,
    K_r,
    K_ESCAPE
)


class ScoreCounter():
    def __init__(self):
        self.hits = 0
        self.all_targets = 0
        self.font_size = 30
        self.font = pygame.freetype.Font(default_font, self.font_size)
        self.shoots = 0
        self.start_time = time.time()
        self.last_hit_time = None
        self.reaction_times = []
    
    def update(self):
        text = f"{self.hits}/{self.all_targets}"
        text_rect = self.font.get_rect(text, size=30) 
        text_rect.midtop = screen.get_rect().midtop
        self.font.render_to(screen, text_rect, text, score_color)

    def add_hit(self):
        self.hits += 1
        if self.last_hit_time:
            reaction = time.time()-self.last_hit_time
            self.reaction_times.append(reaction) 
        self.last_hit_time = time.time()
    
    def add_target(self):
        self.all_targets += 1

    def add_shoot(self):
        self.shoots += 1
    
    # return how much time current round takes
    def get_time(self):
        return round(time.time() - self.start_time, 2)
    
    def get_accuracy(self):
        if self.shoots > 0:
            return round(self.hits*100/self.shoots, 2)
        else:
            return 0.0
    
    def get_hits(self):
        return self.hits
    
    def get_all_targets(self):
        return self.all_targets
    
    def get_median_reaction_time(self):
        def median(data):
            if len(data) == 0: return 0
            data.sort()
            mid = len(data) // 2
            return (data[mid] + data[~mid]) / 2

        return median(self.reaction_times)
    

class Target():
    def __init__(self, start_max=False, forbidden_rects=[]):
        self.forbidden_rects = forbidden_rects
        self.max_radius = 50
        self.reached_max = False
        self.pos = self.get_allowed_pos()
        self.radius = 0
        self.outline_margin = 4
        if start_max:
            self.radius = self.max_radius
    
    def update(self):
        if self.radius < self.max_radius and not self.reached_max:
            self.radius += 1
        else:
            self.reached_max = True
            self.radius -= 1
            # destroy this object if smaller than 1px
            if self.radius <= 0:
                return False 
        self.draw()

    def draw(self):
        # draw outline
        pygame.draw.circle(screen, outline_color, self.pos, self.radius, self.outline_margin)
        # draw filling
        pygame.draw.circle(screen, filling_color, self.pos, self.radius-self.outline_margin)

    def mouse_collides(self, mouse_pos):
        if pow((mouse_pos[0] - self.pos[0]), 2) + pow((mouse_pos[1] - self.pos[1]), 2) <= pow(self.radius, 2):
            return True
    
    def get_random_pos(self, margin=0):
        x = random.randint(margin, SCREEN_WIDTH-margin)
        y = random.randint(margin, SCREEN_HEIGHT-margin)
        return (x, y)
    
    # get free space for spawn
    def get_allowed_pos(self):
        for i in range(200): # to prevent freezing if there is no more space for targets
            pos = self.get_random_pos(self.max_radius)
            if not self.rect_in_forbidden_area(pos):
                return pos
        return (100, 100)

    # check if targets would overlap
    def rect_in_forbidden_area(self, pos):
        rect_to_check = self.get_final_rect(pos)
        for rect in self.forbidden_rects:
            if rect.colliderect(rect_to_check):
                return True
        return False
    
    # get max occupied space as rect
    def get_final_rect(self, center=None):
        rect = pygame.Rect((0, 0), (self.max_radius*2, self.max_radius*2))
        if center == None:
            rect.center = self.pos
        else:
            rect.center = center
        return rect


# Button with an outline and a callback
class Button(): 
    def __init__(self, font, text, text_color, text_rect, padding=0, outline_color=(0,0,0), outline_radius=0, custom_outline_rect=None):
        if custom_outline_rect:
            self.button_rect = pygame.draw.rect(screen, outline_color, custom_outline_rect, outline_radius)
        else:
            self.button_rect = pygame.draw.rect(screen, outline_color, text_rect.inflate(padding, padding), outline_radius)
        self.text_rect = font.render_to(screen, text_rect, text, text_color)

    def set_callback(self, callback, *args, **kwargs):
        self.callback = callback
        self.callback_args = args
        self.callback_kwargs = kwargs

    def check_click(self, mouse_pos):
        if self.button_rect:
            if self.button_rect.collidepoint(mouse_pos):
                self.callback(*self.callback_args, **self.callback_kwargs)


class Game():
    def __init__(self):
        self.events = {}
        self.change_game_mode("Lobby")

    def change_game_mode(self, game_mode):
        if game_mode == "Lobby":
            self.game_mode_obj = gamemodes.Lobby(screen, self)
        elif game_mode == "Summary":
            self.game_mode_obj = gamemodes.Summary(screen, self)
        elif game_mode == "Arcade":
            self.game_mode_obj = gamemodes.Arcade(screen, self)
        elif game_mode == "Speedy fingers":
            self.game_mode_obj = gamemodes.SpeedyFingers(screen, self)
        else:
            raise Exception("There is no provided game mode: " + str(game_mode))
        self.game_mode_obj.load()
        self.game_mode = game_mode
    
    def reset(self):
        for event in self.events.values():
            pygame.time.set_timer(event, 0)
        self.scoreCounter = ScoreCounter()

    def frame(self):
        self.game_mode_obj.frame()

    def add_target(self, start_max=False, forbidden_rects=[]):
        return Target(start_max=start_max, forbidden_rects=forbidden_rects)


# BASE SETTINGS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# PYGAME INIT
pygame.init()
pygame.display.set_caption('aimbooster v.0.0.2')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# LOAD GAME
game = Game()

# GAME EVENTS
game.events["ADD_TARGET"] = USEREVENT + 1

# GAME MECHANICS
game.TARGET_SPAWNRATE = 3 # targets per second 

# MAINLOOP
running = True
while running:
    for event in pygame.event.get((QUIT, KEYDOWN)):
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_s or event.key == K_ESCAPE:
                # return to prevent updating screen with targets after summary shows up
                game.change_game_mode("Summary")
                continue
            elif event.key == K_r:
                game.change_game_mode(game.game_mode)
                continue
    game.frame()
    # refresh display
    pygame.display.update()
    clock.tick(FPS)
pygame.quit()


# todo
# - add training modes
# - save stats